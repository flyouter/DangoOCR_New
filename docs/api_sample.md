```shell
curl --location --request POST 'http://localhost:26467/ocr/api' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: localhost:26467' \
--header 'Connection: keep-alive' \
--data-raw '{
    "ImagePath":"G:/pythonProject/DangoOCR/test/JAP.jpg",
    "Language":"JAP"
}'
```





response:

```json
{
    "Code": 0,
    "Data": [
        {
            "Coordinate": {
                "LowerLeft": [
                    21.0,
                    41.0
                ],
                "LowerRight": [
                    884.0,
                    41.0
                ],
                "UpperLeft": [
                    21.0,
                    17.0
                ],
                "UpperRight": [
                    884.0,
                    17.0
                ]
            },
            "Score": 0.9582222700119019,
            "Words": "校門の外から携てた様子でやってきた二人組の男たちに声をかけられるとちらも"
        },
        {
            "Coordinate": {
                "LowerLeft": [
                    20.0,
                    69.0
                ],
                "LowerRight": [
                    780.0,
                    72.0
                ],
                "UpperLeft": [
                    20.0,
                    44.0
                ],
                "UpperRight": [
                    780.0,
                    47.0
                ]
            },
            "Score": 0.9711936712265015,
            "Words": "中年くらいで、一人はバカでかいピデオカメラのような機材を担いでいた。"
        },
        {
            "Coordinate": {
                "LowerLeft": [
                    22.0,
                    85.0
                ],
                "LowerRight": [
                    33.0,
                    85.0
                ],
                "UpperLeft": [
                    22.0,
                    75.0
                ],
                "UpperRight": [
                    33.0,
                    75.0
                ]
            },
            "Score": 0.6786454319953918,
            "Words": "し"
        }
    ],
    "Message": "Success",
    "RequestId": "a23eed82-485d-4fe0-8801-2abcb5184de0"
}
```