import argparse

import torch
import os

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
from trainer import build_trainer
from utils import (  # noqa
    collect_env_info,
    get_cfg_default,
    set_random_seed,
    setup_logger,
)


def reset_cfg_from_args(cfg, args):
    # ====================
    # Reset Global CfgNode
    # ====================
    cfg.GPU = args.gpu
    cfg.OUTPUT_DIR = args.output_dir
    cfg.SEED = args.seed
    cfg.DATASET.ROOT = args.root

    # ====================
    # Reset Dataset CfgNode
    # ====================
    if args.dataset:
        cfg.DATASET.NAME = args.dataset
    if args.source_domains:
        cfg.DATASET.SOURCE_DOMAINS = args.source_domains
    if args.target_domains:
        cfg.DATASET.TARGET_DOMAINS = args.target_domains

    # ====================
    # Reset Model CfgNode
    # ====================
    if args.model:
        cfg.MODEL.NAME = args.model


def clean_cfg(cfg, model):
    """Remove Unused Model Configs


    Args:
        cfg (_C): Config Node.
        model (str): model name.
    """
    # Determine active model name (fallback to cfg when args.model is None)
    model_name = model or cfg.MODEL.NAME

    keys = list(cfg.MODEL.keys())
    # Preserve common top-level model settings required by the training/loss pipeline
    preserve_keys = {
        "NAME",
        model_name,
        "METRIC_LOSS_TYPE",
        "NO_MARGIN",
        "IF_LABELSMOOTH",
        "ID_LOSS_WEIGHT",
        "TRIPLET_LOSS_WEIGHT",

    }
    for key in keys:
        if key in preserve_keys:
            continue
        cfg.MODEL.pop(key, None)


def setup_cfg(args):
    cfg = get_cfg_default()

    if args.model_config_file:
        cfg.merge_from_file(args.model_config_file)

    reset_cfg_from_args(cfg, args)

    clean_cfg(cfg, args.model)

    cfg.freeze()

    return cfg


def print_args(args, cfg):
    print("***************")
    print("** Arguments **")
    print("***************")
    optkeys = list(args.__dict__.keys())
    optkeys.sort()
    for key in optkeys:
        print("{}: {}".format(key, args.__dict__[key]))
    print("************")
    print("** Config **")
    print("************")
    print(cfg)


def main(args):
    cfg = setup_cfg(args)

    zero_shot_models = ["CLIPZeroShot", "SIGLIPZeroShot"]

    if cfg.SEED >= 0:
        set_random_seed(cfg.SEED)

    if torch.cuda.is_available() and cfg.GPU >= 0:
        device = torch.device(f'cuda:{cfg.GPU}')
        torch.cuda.set_device(cfg.GPU)
        print(f"Using GPU: {torch.cuda.get_device_name(cfg.GPU)}")
    else:
        device = torch.device('cpu')
        print("WARNING: CUDA not available or GPU < 0, using CPU")
        if cfg.GPU >= 0:
            print("You specified --gpu but CUDA is not available!")

    setup_logger(cfg.OUTPUT_DIR)

    print("*** Config ***")
    print_args(args, cfg)

    # print("Collecting env info ...")
    # print("** System info **\n{}\n".format(collect_env_info()))

    trainer = build_trainer(cfg)
    
    print(f"\nTrainer device: {trainer.device}")
    if hasattr(trainer, 'model'):
        model_device = next(trainer.model.parameters()).device
        print(f"Model device: {model_device}")
        
    if args.model in zero_shot_models:
        trainer.test()
    else:
        trainer.train()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--root", type=str, default="./data/")
    parser.add_argument("--output-dir", type=str, default="./output/")
    parser.add_argument("--dataset", type=str)
    parser.add_argument("--source-domains", type=str, nargs="+")
    parser.add_argument("--target-domains", type=str, nargs="+")
    parser.add_argument("--model", type=str)
    parser.add_argument("--model-config-file", type=str)

    args = parser.parse_args()
    main(args)
