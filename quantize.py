import os
from optimum.onnxruntime import ORTQuantizer, ORTModelForVision2Seq
from optimum.onnxruntime.configuration import AutoQuantizationConfig


def quantize(args):
    onnx_model_path = f'{args.model_path}_onnx'

    model_files = ["encoder_model.onnx", "decoder_model.onnx", "decoder_model_merged.onnx", "decoder_with_past_model.onnx"]
    quantizers = []
    for model_file in model_files:
        quantizer = ORTQuantizer.from_pretrained(onnx_model_path, file_name=model_file)  
        quantizers.append(quantizer)
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=args.per_channel)

    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

    for q in quantizers:
        q.quantize(save_dir=args.save_path, quantization_config=qconfig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--per_channel", type=bool, default='store_true', required=False)
    parser.add_argument("--save_path", type=str, default='./models/donut_quantized', required=False)
    args, _ = parser.parse_known_args()
    
    os.system(f'optimum-cli export onnx --model {args.model_path} --task image-to-text-with-past {args.model_path}_onnx/')

    quantize(args)