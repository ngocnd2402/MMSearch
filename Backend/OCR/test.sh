CUDA_VISIBLE_DEVICES=0 python mmocr/utils/ocr.py /home/visedit/AIC2023/Backend/OCR/mmocr/demo/resources \
            --det DBPP_r50 \
            --det-ckpt /home/visedit/AIC2023/Backend/OCR/mmocr/pretrained/best_0_hmean-iou:hmean_epoch_700.pth \
            --recog None \
            --export /home/visedit/AIC2023/Backend/OCR/mmocr/test \
            --det-batch-size 512