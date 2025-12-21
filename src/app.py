import argparse
import uuid
from traceback import print_exc

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from paddleocr import PaddleOCR

# 2.3版本可用
# paddleocr.paddleocr.BASE_DIR = "./"
MODEL_CACHE ="./paddleocr"
japOcr = PaddleOCR(ocr_version="PP-OCRv5", use_doc_unwarping=False, use_textline_orientation=False, lang="japan",
                   enable_mkldnn=True)
engOcr = PaddleOCR(ocr_version="PP-OCRv5", use_doc_unwarping=False, use_textline_orientation=False, lang="en",
                   enable_mkldnn=True)
korOcr = PaddleOCR(ocr_version="PP-OCRv5", use_doc_unwarping=False, use_textline_orientation=False, lang="korean",
                   enable_mkldnn=True)
ruOcr = PaddleOCR(ocr_version="PP-OCRv5", use_doc_unwarping=False, use_textline_orientation=False, lang="ru",
                  enable_mkldnn=True)
zhOcr = PaddleOCR(ocr_version="PP-OCRv5", use_doc_unwarping=False, use_textline_orientation=False, lang="ch",
                  enable_mkldnn=True)

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
        result = japOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)
    elif language == "ENG":
        result = engOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)
    elif language == "KOR":
        result = korOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)
    elif language == "RU":
        result = ruOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)
    elif language == "ZH":
        result = zhOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)
    else:
        result = japOcr.ocr(imgPath,use_doc_unwarping=False,use_textline_orientation=False)

    resMapList = []

    # PaddleOCR 3.x版本返回结构变化处理
    if result and len(result) > 0:
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
                resMapList.append(resMap)
        else:
            # 旧版本结构处理（兼容性）
            try:
                result = ocrResultSort(result)
            except Exception:
                pass

            for line in result:
                try:
                    print(line[1][0])
                except Exception:
                    pass
                # 检查line结构，防止KeyError
                if isinstance(line, list) and len(line) >= 2:
                    if isinstance(line[0], list) and len(line[0]) >= 4:
                        resMap = {
                            "Coordinate": {
                                "UpperLeft": line[0][0],
                                "UpperRight": line[0][1],
                                "LowerRight": line[0][2],
                                "LowerLeft": line[0][3]
                            },
                            "Words": line[1][0] if isinstance(line[1], list) and len(line[1]) >= 1 else "",
                            "Score": float(line[1][1]) if isinstance(line[1], list) and len(line[1]) >= 2 else 0.0
                        }
                        resMapList.append(resMap)
                    else:
                        print(f"警告: line[0]结构异常: {line}")
                else:
                    print(f"警告: line结构异常: {line}")

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
