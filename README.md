# DonutMathHWP
DonutMathHWP는 수식을 포함한 수학 문제와 해설 이미지에서 HWP 수식을 자동 처리하는 도구로, End-to-End 모델을 활용한 수학 문제 OCR을 수행합니다.  
이 프로젝트는 데이터셋 생성, 모델 학습, 한글 문서 자동화 예제 등을 포함한 다양한 기능을 제공합니다.

## 📚 Project Overview
+ 모델: Donut 아키텍처를 기반으로 하여 HWP 데이터셋에 대해 미세 조정된 모델입니다.
+ 학습 과정: Nougat 데이터셋으로 모델이 이미지에서 글을 읽는 방법을 학습하였고, HWP 데이터셋으로 수식 인식이 학습되었습니다.

## 🔑 Key Features
- **수학 문제 데이터셋 생성**: 한글 파일으로 부터 학습에 필요한 데이터를 생성하고 전처리합니다.
- **모델 학습 및 평가**: 설정 파일을 사용하여 모델을 학습시키고 평가합니다.
- **한글 문서 자동화** : 수식을 포함한 문제를 한글 문서로 자동화 합니다.
- **Jupyter Notebook 튜토리얼**: 프로젝트 사용 방법을 안내하는 예제와 튜토리얼을 제공합니다.

## 📝 Result
**윗 첨자, 아랫 첨자, 분수 표현 결과**  
<img src="https://github.com/user-attachments/assets/7740ef10-ba17-450e-8096-9c37ef99a029" width="50%"/>

```
3. 정적분 $int _{0} ^{2} {LEFT | x ^{2} -1 RIGHT |} dx$의 값은?
① ${1} over {2}$
② $1$
③ ${3} over {2}$
④ $2$
⑤ ${5} over {2}$
```

**로만체 표현 결과**  
<img src="https://github.com/user-attachments/assets/853dd200-d460-4aa4-8195-b6f54b836276" width="50%"/>

```
8. 삼각형 $rm ABC$에서 $bar{rmAB}=2$, $angle rmB=90DEG$, $angle rmC=30DEG$이다. 점 $rmP$가 $rm vec{PB} +vec{PC} = vec0$를 만족시킬 때, $rm {left| vec{PA } right|}^{2}$의 값은?
[2012학년도 수능]
① $5$② $6$③ $7$④ $8$⑤ $9$
```

**이미지가 포함된 문제 예시**  
<img src="https://github.com/user-attachments/assets/127f20bc-c80e-432b-9465-cdb8f9fc63cb" width="50%"/>

```
12. 이차함수 $y=f(x)$와 삼차함수 $y=g(x)$의 그래프가 그림과 같다.
$f(-1)=f(3)=0$이고, 함수 $g(x)$가 $x=3$에서 극솟값 $-2$를 가질 때, 방정식 ${g(x)+2} over f(x) - 2 over g(x) =1$의 서로 다른 실근의 개수는?
[3점][2012학년도 수능]
① $1$
② $2$
③ $3$
④ $4$
⑤ $5$
```

## ⚡ Demo
+ HuggingFace [space](https://huggingface.co/spaces/sooooner/DonutMathHWP)를 통해 실제 결과를 확인 가능합니다.
+ hwp 자동화 [demo](http://hwpmath.duckdns.org/)를 통해 실제 문제 또는 해설 이미지를 한글 파일로 변환 가능

### 🖥️ Installation & Execution
1. 프로젝트 설치
    ```bash
    git clone https://github.com/sooooner/DonutMathHWP.git
    cd DonutMathHWP
    pip install -r requirements.txt
    ```
2. 데이터셋 생성  
모의고사 시험문제 한글 파일로 부터 데이터셋을 생성합니다.  
데이터셋 생성은 **pywin32**을 사용하며 **window OS**에서 실행 가능합니다.
   + 데이터셋 생성을 위해 모의고사 hwp 파일을 `dataste/mock_exam_data` 디렉토리에 수집합니다.
   + hwp 파일으로 부터 이미지와 텍스트를 추출하기 위해서 `dataset/hwp_processing.py` 실행 합니다.
   + 추출된 데이터로 부터 훈련데이터 생성을 위해 `create_datasets.py` 실행 합니다.
    ```bash
    python -m dataset.hwp_processing
    python create_datasets.py
    ```
3. 모델 학습  
데이터 생성이 완료되면 다음과 같이 설정 파일을 사용해 모델을 학습시킵니다.
    ```bash
    python train.py --config=config/train_config.json
    ```
    학습 결과  
    <img src="https://github.com/user-attachments/assets/ff9d4281-3b3b-4b36-9919-b88670f29d95" width="90%"/>

4. 한글 문서 자동화  
   + `AutoHWP_Tutorial.ipynb`를 통해 한글 문서 자동화를 실행할 수 있습니다.
   + 모델을 학습하지 않아도 HuggingFace에서 사전 학습된 모델을 받아 활용할 수 있습니다.  

### 📖 Reference
이 프로젝트는 다음 논문들을 바탕으로 하고 있습니다:  
+ [Donut]((https://github.com/clovaai/donut)): OCR-Free Document Understanding Transformer 
+ [Nougat]((https://github.com/facebookresearch/nougat)): Neural Optical Understanding for Academic Documents

### 💡 Future Improvements
+ 문제 형식 이외에 해설 형식 지원 `[v]`
+ 사용자가 더 편리하게 이용할 수 있도록 웹 인터페이스를 개선하고 있습니다. `[진행 중]`
+ 수학 이외의 과목 문제 인식 기능 추가.

