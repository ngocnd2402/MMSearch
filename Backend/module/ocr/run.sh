KEYFRAME_DIR_LV_0=/YOUR_KEYFRAME/DIR
RES_DIR_LV_0=/ocr/infer-new
CROPPED_FOLDER=/ocr/mmocr/inference-result/crop-image
DROPPED_FOLDER=/ocr/mmocr/inference-result/drop-image
JSON_FOLDER=/ocr/mmocr/inference-result/json
PARSEQ_FILE=rec_result.txt

rm -rf $CROPPED_FOLDER
mkdir $CROPPED_FOLDER

rm -rf $DROPPED_FOLDER
mkdir $DROPPED_FOLDER

rm -rf $JSON_FOLDER
mkdir $JSON_FOLDER

for dir_lv_1 in $(ls $KEYFRAME_DIR_LV_0)
do
    echo $dir_lv_1

    if [[ "$dir_lv_1" > "L35" ]]; then
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
        eval "$(conda shell.bash hook)"
        conda activate openmmlab
        cd mmocr
        CUDA_VISIBLE_DEVICES=0 python mmocr/utils/ocr.py $KEYFRAME_DIR_LV_2 \
            --det DBPP_r50 \
            --det-ckpt /DBNET_CKPT_PATH \
            --recog None \
            --export $JSON_FOLDER \
            --det-batch-size 512
        cd ..
        python crop_image.py \
            $KEYFRAME_DIR_LV_2 \
            $JSON_FOLDER \
            $CROPPED_FOLDER \
            $DROPPED_FOLDER
        eval "$(conda shell.bash hook)"
        conda activate parseq
        cd parseq
        python read.py '/PARSEQ_CKPT_PATH' \
            --images $CROPPED_FOLDER \
            --outfile $PARSEQ_FILE
        cd ..
        cp /ocr/parseq/$PARSEQ_FILE $RES_FILE
        rm -rf $CROPPED_FOLDER
        mkdir $CROPPED_FOLDER
        rm -rf $DROPPED_FOLDER
        mkdir $DROPPED_FOLDER
        rm -rf $JSON_FOLDER
        mkdir $JSON_FOLDER
    done 
done
