# DonutMathHWP

DonutMathHWP는 수식을 포함한 수식 이미지에서 hwp수식 처리를 위한 도구로, End-to-End 모델을 활용하여 수학 문제 OCR을 수행합니다.  
이 프로젝트는 데이터셋 생성, 모델 학습, 양자화, 그리고 한글 자동화 예제를 포함한 다양한 기능을 제공합니다.

## 주요 기능
- **수학 문제 데이터셋 생성**: 한글 파일으로 부터 학습에 필요한 데이터를 생성하고 전처리합니다.
- **모델 학습 및 평가**: 설정 파일을 사용하여 모델을 학습시키고 평가합니다.
- **양자화 및 모델 최적화**: 모델의 효율성을 높이기 위해 양자화 과정을 지원합니다.
- **한글 문서 자동화** : 수식을 포함한 문제를 한글 문서로 자동화 합니다.
- **Jupyter Notebook 튜토리얼**: 프로젝트 사용 방법을 안내하는 예제와 튜토리얼을 제공합니다.

## 시작하기
+ HuggingFace [space](https://huggingface.co/spaces/sooooner/HanOCRMath)를 통해 demo 확인

### 설치

아래 명령어를 통해 프로젝트를 설치할 수 있습니다:

```bash
git clone https://github.com/sooooner/DonutMathHWP.git
cd DonutMathHWP
pip install -r requirements.txt
```cdc

### 데이터셋 생성
1. 데이터셋 생성을 위해 모의고사 hwp 파일을 dataste/mock_exam_data 디렉토리에 수집합니다.
2. hwp 파일으로 부터 이미지와 텍스트를 추출하기 위해서 dataset/hwp_processing.py 실행 합니다.
    + openai api key 필요
3. 추출된 데이터로 부터 훈련데이터 생성을 위해 create_datasets.py 실행
```bash
python dataset/hwp_processing.py 
python create_datasets.py
```

### 모델 학습
```bash
python train.py --config=config/train_config.json
```

## 사용 예시
AutoHWP_Tutorial.ipynb를 통해 한글 문서 자동화 실행.  
모델을 학습하지 않아도 [HuggingFace](https://huggingface.co/sooooner/donut-math-small-quantized) 모델을 받아서 활용가능합니다.


### **Reference**
이 프로젝트는 다음 논문들을 바탕으로 하고 있습니다:  
+ [Donut]((https://github.com/clovaai/donut)): OCR-Free Document Understanding Transformer 
+ [Nougat]((https://github.com/facebookresearch/nougat)): Neural Optical Understanding for Academic Documents
