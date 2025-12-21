import argparse
import os
import sys
import uuid
from traceback import print_exc

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from paddleocr import PaddleOCR


def get_base_dir():
    """获取基础目录，兼容开发环境和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境，使用临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发环境，使用项目根目录
        # 注意：在打包后的环境中，__file__可能不可用
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except:
            base_path = os.getcwd()
    return base_path


def create_ocr_instance(lang, det_model_name, rec_model_name):
    """
    创建OCR实例，如果模型目录不存在则自动下载到models目录
    """
    # 获取基础目录
    base_dir = get_base_dir()
    base_model_dir = os.path.join(base_dir, "models")
    det_model_dir = os.path.join(base_model_dir, det_model_name)
    rec_model_dir = os.path.join(base_model_dir, rec_model_name)

    # 模型目录存在，使用本地模型
    # print(f"基础目录: {base_dir}")
    # print(f"模型目录: {base_model_dir}")
    print(f"使用本地模型: {det_model_dir}, {rec_model_dir}")
    return PaddleOCR(
        text_detection_model_dir=det_model_dir,
        text_recognition_model_dir=rec_model_dir,
        text_recognition_model_name=rec_model_name,
        text_detection_model_name=det_model_name,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        lang=lang,
        enable_mkldnn=True
    )


# 创建各个语言的OCR实例
japOcr = create_ocr_instance("japan", "PP-OCRv5_server_det", "PP-OCRv5_mobile_rec")
engOcr = create_ocr_instance("en", "PP-OCRv5_server_det", "PP-OCRv5_server_rec")
korOcr = create_ocr_instance("korean", "PP-OCRv5_server_det", "korean_PP-OCRv5_mobile_rec")
ruOcr = create_ocr_instance("ru", "PP-OCRv5_server_det", "eslav_PP-OCRv5_mobile_rec")
zhOcr = create_ocr_instance("ch", "PP-OCRv5_server_det", "PP-OCRv5_server_rec")

app = FastAPI()


# 请求模型
class OCRRequest(BaseModel):
    ImagePath: str
    Language: str


# 坐标模型
class Coordinate(BaseModel):
    UpperLeft: list[float]
    UpperRight: list[float]
    LowerRight: list[float]
    LowerLeft: list[float]


# 响应模型
class OCRResult(BaseModel):
    Coordinate: Coordinate
    Words: str
    Score: float


class SuccessResponse(BaseModel):
    Code: int = 0
    Message: str = "Success"
    RequestId: str
    Data: list[OCRResult]


class FailResponse(BaseModel):
    Code: int = -1
    Message: str
    RequestId: str


# 失败的返回
def jsonFail(message):
    post_data = {
        "Code": -1,
        "Message": str(message),
        "RequestId": str(uuid.uuid4())
    }
    return JSONResponse(content=post_data)


# 成功的返回
def jsonSuccess(data):
    post_data = {
        "Code": 0,
        "Message": "Success",
        "RequestId": str(uuid.uuid4()),
        "Data": data
    }
    return JSONResponse(content=post_data)


def ocrResultSort(ocr_result):
    ocr_result.sort(key=lambda x: x[0][0][1])

    # 二次根据纵坐标数值分组（分行）
    all_group = []
    new_group = []
    flag = ocr_result[0][0][0][1]
    pram = max([int((i[0][3][1] - i[0][0][1]) / 2) for i in ocr_result])

    for sn, i in enumerate(ocr_result):
        if abs(flag - i[0][0][1]) <= pram:
            new_group.append(i)
        else:
            all_group.append(new_group)
            flag = i[0][0][1]
            new_group = [i]
    all_group.append(new_group)

    # 单行内部按左上点横坐标排序
    all_group = [sorted(i, key=lambda x: x[0][0][0]) for i in all_group]
    # 去除分组，归一为大列表
    all_group = [ii for i in all_group for ii in i]
    # 列表输出为排序后txt
    all_group = [ii for ii in all_group]

    return all_group


# ocr解析
def ocrProcess(imgPath, language):
    if language == "JAP":
        result = japOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)
    elif language == "ENG":
        result = engOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)
    elif language == "KOR":
        result = korOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)
    elif language == "RU":
        result = ruOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)
    elif language == "ZH":
        result = zhOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)
    else:
        result = japOcr.ocr(imgPath, use_doc_unwarping=False, use_textline_orientation=False)

    resMapList = []

    ocr_result = result[0]

    # 检查是否是字典结构（PaddleOCR 3.x版本）
    if isinstance(ocr_result, dict):
        # 从字典中提取数据
        texts = ocr_result.get('rec_texts', [])
        scores = ocr_result.get('rec_scores', [])
        boxes = ocr_result.get('rec_boxes', [])

        for i in range(len(texts)):
            text = texts[i] if i < len(texts) else ""
            score = float(scores[i]) if i < len(scores) else 0.0

            # 处理坐标框
            coord = {
                "UpperLeft": [0.0, 0.0],
                "UpperRight": [0.0, 0.0],
                "LowerRight": [0.0, 0.0],
                "LowerLeft": [0.0, 0.0]
            }

            if i < len(boxes):
                box = boxes[i]
                # PaddleOCR 3.x版本box可能是4个整数值 [x1, y1, x2, y2]
                if hasattr(box, '__len__') and len(box) == 4:
                    # 转换为4个坐标点
                    x1, y1, x2, y2 = box
                    coord = {
                        "UpperLeft": [float(x1), float(y1)],
                        "UpperRight": [float(x2), float(y1)],
                        "LowerRight": [float(x2), float(y2)],
                        "LowerLeft": [float(x1), float(y2)]
                    }
                elif hasattr(box, 'shape') and box.shape == (4, 2):
                    # 4x2坐标点格式
                    coord = {
                        "UpperLeft": [float(box[0][0]), float(box[0][1])],
                        "UpperRight": [float(box[1][0]), float(box[1][1])],
                        "LowerRight": [float(box[2][0]), float(box[2][1])],
                        "LowerLeft": [float(box[3][0]), float(box[3][1])]
                    }

            resMap = {
                "Coordinate": coord,
                "Words": text,
                "Score": score
            }
            print("score:", score)
            print(text)
            resMapList.append(resMap)

    print(f"识别结果数: {len(resMapList)}")
    return resMapList


# 接收请求
@app.post("/ocr/api")
async def handle_request(request_data: OCRRequest):
    try:
        languageList = ["JAP", "ENG", "KOR", "RU", "ZH"]
        if request_data.Language not in languageList:
            return jsonFail("Language {} doesn't exist".format(request_data.Language))

        res = ocrProcess(request_data.ImagePath, request_data.Language)
        return jsonSuccess(res)

    except Exception as err:
        print_exc()
        return jsonFail(str(err))


# HEAD请求用于客户端检测
@app.head("/ocr/api")
async def handle_head_request():
    from fastapi.responses import Response
    return Response(headers={"Dango-OCR": "OK"})


if __name__ == "__main__":
    import uvicorn

    host = "127.0.0.1"
    port = 43623
    path = "/ocr/api"

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--host", type=str, default=host, help="监听的主机。默认：\"%s\"" % host)
    parser.add_argument("-p", "--port", type=int, default=port, help="监听的端口。默认：%d" % port)
    parser.add_argument("-P", "--path", type=str, default=path, help="监听的路径。默认：\"%s\"" % path)

    parser.add_argument('--help', action='help', help='打印帮助。')
    args = parser.parse_args()

    host = args.host
    port = args.port
    print("监听：http://%s:%d/ocr/api" % (host, port))
    uvicorn.run(app, host=host, port=port)
