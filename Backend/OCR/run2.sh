KEYFRAME_DIR_LV_0=/mmlabworkspace/Students/visedit/AIC2023/Data/Reframe
RES_DIR_LV_0=/mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/infer-new

CROPPED_FOLDER=/mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/mmocr/inference-result/crop-image2
DROPPED_FOLDER=/mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/mmocr/inference-result/drop-image2
JSON_FOLDER=/mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/mmocr/inference-result/json2
PARSEQ_FILE=rec_result2.txt

rm -rf $CROPPED_FOLDER
mkdir $CROPPED_FOLDER

rm -rf $DROPPED_FOLDER
mkdir $DROPPED_FOLDER

rm -rf $JSON_FOLDER
mkdir $JSON_FOLDER

for dir_lv_1 in $(ls $KEYFRAME_DIR_LV_0)
do
    echo $dir_lv_1

    if [[ "$dir_lv_1" < "L11" || "$dir_lv_1" > "L20" ]]; then
        continue
    fi

    KEYFRAME_DIR_LV_1=$KEYFRAME_DIR_LV_0/$dir_lv_1
    RES_DIR_LV_1=$RES_DIR_LV_0/$dir_lv_1

    mkdir $RES_DIR_LV_1

    for dir_lv_2 in $(ls $KEYFRAME_DIR_LV_1)
    do
        echo $dir_lv_2

        KEYFRAME_DIR_LV_2=$KEYFRAME_DIR_LV_1/$dir_lv_2
        RES_FILE=$RES_DIR_LV_1/$dir_lv_2.txt

        # mmocr
        # source /home/visedit/.conda/bin/activate openmmlab
        eval "$(conda shell.bash hook)"
        conda activate openmmlab

        # conda activate openmmlab
        cd mmocr
        CUDA_VISIBLE_DEVICES=0 python mmocr/utils/ocr.py $KEYFRAME_DIR_LV_2 \
            --det DBPP_r50 \
            --det-ckpt /mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/mmocr/pretrained/best_0_hmean-iou:hmean_epoch_700.pth \
            --recog None \
            --export $JSON_FOLDER \
            --det-batch-size 512
            # --output /mmlabworkspace/Students/ngoc_AIC2023/Backend/OCR/mmocr/inference-result/visualization \

        cd ..

        # crop images
        python crop_image.py \
            $KEYFRAME_DIR_LV_2 \
            $JSON_FOLDER \
            $CROPPED_FOLDER \
            $DROPPED_FOLDER

        # parseq
        # source /home/visedit/.conda/bin/activate parseq
        eval "$(conda shell.bash hook)"
        conda activate parseq
        # conda activate parseq
        cd parseq
        python read.py '/mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/parseq/pretrained/epoch=79-step=9230-val_accuracy=88.3849-val_NED=95.1411.ckpt' \
            --images $CROPPED_FOLDER \
            --outfile $PARSEQ_FILE

        cd ..

        # final result
        cp /mmlabworkspace/Students/visedit/AIC2023/Backend/OCR/parseq/$PARSEQ_FILE $RES_FILE

        # clear temp folders
        rm -rf $CROPPED_FOLDER
        mkdir $CROPPED_FOLDER

        rm -rf $DROPPED_FOLDER
        mkdir $DROPPED_FOLDER

        rm -rf $JSON_FOLDER
        mkdir $JSON_FOLDER
    done 
done
