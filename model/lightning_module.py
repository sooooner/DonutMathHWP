import re
import torch
import numpy as np
import pytorch_lightning as pl
from nltk import edit_distance


class DonutModelPLModule(pl.LightningModule):
    def __init__(self, config, model, tokenizer, data_loaders):
        super().__init__()
        self.config = config
        self.model = model
        self.tokenizer = tokenizer
        self.train_dataloader_, self.val_dataloader_ = data_loaders

    def training_step(self, batch, batch_idx):
        pixel_values, labels, _ = batch

        outputs = self.model(pixel_values, labels=labels)
        loss = outputs.loss
        self.log("train_loss", loss, on_step=True)
        return loss

    def validation_step(self, batch, batch_idx, dataset_idx=0):
        pixel_values, labels, answers = batch
        batch_size = pixel_values.shape[0]

        outputs = self.model(pixel_values, labels=labels)
        loss = outputs.loss

        decoder_input_ids = torch.full((batch_size, 1), self.model.config.decoder_start_token_id, device=self.device)

        outputs = self.model.generate(pixel_values,
                                   decoder_input_ids=decoder_input_ids,
                                   max_length=max_length,
                                   early_stopping=True,
                                   pad_token_id=self.tokenizer.pad_token_id,
                                   eos_token_id=self.tokenizer.eos_token_id,
                                   use_cache=True,
                                   num_beams=1,
                                   bad_words_ids=[[self.tokenizer.unk_token_id]],
                                   return_dict_in_generate=True,)

        predictions = []
        for seq in self.tokenizer.batch_decode(outputs.sequences):
            seq = seq.replace(self.tokenizer.eos_token, "").replace(self.tokenizer.pad_token, "")
            seq = re.sub(r"<.*?>", "", seq, count=1).strip()  # remove first task start token
            predictions.append(seq)

        scores = []
        for pixel_value, pred, answer in zip(pixel_values, predictions, answers):
            pred = re.sub(r"(?:(?<=>) | (?=</s_))", "", pred)
            # NOT NEEDED ANYMORE
            # answer = re.sub(r"<.*?>", "", answer, count=1)
            answer = answer.replace(self.tokenizer.eos_token, "")
            scores.append(edit_distance(pred, answer) / max(len(pred), len(answer)))

            if self.config.get("verbose", False) and len(scores) == 1:
                print(f"Prediction: {pred}")
                print(f"    Answer: {answer}")
                print(f" Normed ED: {scores[0]}")
                print()

        self.log("val_loss", loss, on_step=True, on_epoch=True)
        self.log("val_edit_distance", np.mean(scores), on_epoch=True)

        return scores

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.config.get("lr"))
        return optimizer

    def train_dataloader(self):
        return self.train_dataloader_

    def val_dataloader(self):
        return self.val_dataloader_
