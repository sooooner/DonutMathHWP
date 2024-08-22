import os
import torch
import argparse
import datetime
from sconf import Config
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers.file_utils import ModelOutput
from pytorch_lightning.loggers import WandbLogger

import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback, EarlyStopping, LearningRateMonitor
from transformers import DonutProcessor, AutoTokenizer, VisionEncoderDecoderModel
from model import train_transform, DonutModelPLModule, DonutDataset


os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class ProgressBar(pl.callbacks.TQDMProgressBar):
    def __init__(self, config):
        super().__init__()
        self.enable = True
        self.config = config

    def disable(self):
        self.enable = False

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        super().on_train_batch_end(trainer, pl_module, outputs, batch, batch_idx)

        if isinstance(outputs, ModelOutput) and 'loss' in outputs:
            loss = outputs.loss.item()  
        elif isinstance(outputs, dict) and 'loss' in outputs:
            loss = outputs['loss'].item()  
        else:
            loss = None

        if loss is not None:
            self.train_progress_bar.set_postfix({'loss': f'{loss:.4f}'})


class PushToHubCallback(Callback):
    def __init__(self, repo_id):
        super(PushToHubCallback, self).__init__()
        self.repo_id = repo_id

    def on_train_epoch_end(self, trainer, pl_module):
        print(f"Pushing model to the hub, epoch {trainer.current_epoch}")
        pl_module.model.push_to_hub(self.repo_id, commit_message=f"Training in progress, epoch {trainer.current_epoch}")

    def on_train_end(self, trainer, pl_module):
        print(f"Pushing model to the hub after training end")
        pl_module.processor.push_to_hub(self.repo_id, commit_message=f"Training done")
        pl_module.model.push_to_hub(self.repo_id, commit_message=f"Training done")


def load_pretrained_model(config):
    tokenizer = AutoTokenizer.from_pretrained(config.pretrained_model_name_or_path)
    model = VisionEncoderDecoderModel.from_pretrained(config.pretrained_model_name_or_path)
    model.config.encoder.image_size = config.input_size
    model.config.decoder.max_length = config.max_length
    model.config.pad_token_id = tokenizer.pad_token_id

    processor = DonutProcessor.from_pretrained(config.processor_name_or_path)
    processor.image_processor.size = config.input_size
    processor.image_processor.do_align_long_axis = config.align_long_axis
    return tokenizer, model, processor


def load_datasets(config, tokenizer, model, processor):
    dataset = load_dataset(config.dataset_path)
    datasets = dataset['train'].train_test_split(test_size=config.num_validation, seed=config.seed)
    train_dataset = DonutDataset(
        datasets['train'], 
        model=model,
        tokenizer=tokenizer, 
        processor=processor, 
        max_length=config.max_length,
        split="train", 
        task_start_token=config.start_token,
        sort_json_key=config.sort_json_key,
        transform=train_transform
        )

    val_dataset = DonutDataset(
        datasets['test'], 
        model=model,
        tokenizer=tokenizer, 
        processor=processor, 
        max_length=config.max_length,
        split="validation",
        task_start_token=config.start_token,
        sort_json_key=config.sort_json_key
        )

    model.decoder.resize_token_embeddings(len(tokenizer))
    model.config.decoder_start_token_id = tokenizer.convert_tokens_to_ids([config.start_token])[0]

    train_dataloader = DataLoader(train_dataset, batch_size=config.train_batch_size, shuffle=True, num_workers=0)
    val_dataloader = DataLoader(val_dataset, batch_size=config.val_batch_size, shuffle=False, num_workers=0)
    return train_dataloader, val_dataloader


def save_model(model, processor, tokenizer, save_path):
    model.save_pretrained(save_path, save_config=True, state_dict=model.state_dict())
    processor.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    model.config.save_pretrained(save_path)


def train(config):
    tokenizer, model, processor = load_pretrained_model(config)
    data_loaders = load_datasets(config, tokenizer, model, processor)

    torch.cuda.empty_cache()
    model_module = DonutModelPLModule(config, model, tokenizer, data_loaders)
    if config.wandb:
        wandb_logger = WandbLogger(project=config.exp_name, name=config.exp_version)

    lr_callback = LearningRateMonitor(logging_interval="step")
    early_stop_callback = EarlyStopping(monitor="val_edit_distance", patience=3, verbose=False, mode="min")
    bar = ProgressBar(config)
    callbacks = [early_stop_callback, bar, lr_callback]
    if config.repo_id:
        callbacks.append(PushToHubCallback(config.repo_id))

    trainer = pl.Trainer(
            accelerator="gpu",
            devices=1,
            max_epochs=config.get("max_epochs"),
            val_check_interval=config.get("val_check_interval"),
            check_val_every_n_epoch=config.get("check_val_every_n_epoch"),
            gradient_clip_val=config.get("gradient_clip_val"),
            precision=16,
            num_sanity_val_steps=0,
            logger=wandb_logger,
            callbacks=callbacks,
    )

    trainer.fit(model_module)
    save_model(model, processor, tokenizer, save_path=config.save_path)

# python train.py --config config/problems.yaml \
#                 --pretrained_model_name_or_path "facebook/nougat-base" \
#                 --processor_name_or_path "naver-clova-ix/donut-base" \
#                 --dataset_path "path/to/dataset" \
#                 --save_path "path/to/save" \
#                 --repo_id "huggingface/push/repo" \
#                 --wandb True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--pretrained_model_name_or_path", type=str, required=True)
    parser.add_argument("--processor_name_or_path", type=str, required=True)
    parser.add_argument("--dataset_path", type=str, required=True)
    parser.add_argument("--save_path", type=str, required=True)
    parser.add_argument("--repo_id", type=str, required=False)
    parser.add_argument("--wandb", type=bool, required=False)
    parser.add_argument("--exp_version", type=str, required=False)
    args, left_argv = parser.parse_known_args()

    config = Config(args.config)
    config.argv_update(left_argv)
    config.update({
        "pretrained_model_name_or_path": args.pretrained_model_name_or_path,
        "processor_name_or_path": args.processor_name_or_path,
        "dataset_path": args.dataset_path,
        "save_path": args.save_path,
        "repo_id": args.repo_id,
        "wandb": args.wandb
    })
    if args.wandb:
        config.exp_name = basename(args.config).split(".")[0]
        config.exp_version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") if not args.exp_version else args.exp_version

    train(config)