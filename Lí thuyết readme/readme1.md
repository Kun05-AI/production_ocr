trình bày về hugging face là gì ? safetensors ? Transformer ? Qwen3-VL-4B-Instruct  ? Thuật ngữ về API nữa, tao không hiểu lắm, mấy anh chị cứ kêu gọi api gemini mà tao chả hiểu

Ừ, mấy cái này lúc mới bước vào AI rất dễ bị rối thành một nồi thuật ngữ =))) Thực ra chúng nằm ở các tầng khác nhau. Tao sẽ xếp từ dễ → sâu, rồi nối chúng lại thành một quy trình để mày hình dung.

1. Nhìn tổng thể trước

Mày có thể hình dung thế này:

                    AI / LLM
                       │
             ┌─────────┴─────────┐
             │                   │
        Mô hình AI            API AI
             │                   │
     ┌───────┴───────┐       Gemini API
     │               │       OpenAI API
 Transformer      Qwen3-VL
     │               │
     │          model weights
     │               │
     │          safetensors
     │
 Hugging Face

Hugging Face = nền tảng/hệ sinh thái để người ta đăng, tải, chia sẻ và chạy model.

Transformer = một kiến trúc neural network rất quan trọng, nền tảng của phần lớn LLM hiện đại.

Qwen3-VL-4B-Instruct = một model cụ thể.

Safetensors = định dạng file lưu trọng số model.

API = cách một chương trình gọi chức năng/dữ liệu của một hệ thống khác.

Còn:

"Gọi API Gemini"

nghĩa đơn giản là:

Code của mày gửi yêu cầu lên server của Google → Gemini xử lý → Google trả kết quả về cho code của mày.

2. Hugging Face là gì?

Hugging Face là một nền tảng + hệ sinh thái AI/ML.

Nó khá giống GitHub nhưng dành rất nhiều cho machine learning.

Ví dụ GitHub:

GitHub
 ├── source code
 ├── README
 ├── issues
 └── releases

Hugging Face:

Hugging Face
 ├── Models
 ├── Datasets
 ├── Spaces
 ├── Libraries
 └── Model documentation

Ví dụ một người tạo model:

Qwen/
└── Qwen3-VL-4B-Instruct
      ├── config.json
      ├── tokenizer.json
      ├── model-00001-of-00002.safetensors
      ├── model-00002-of-00002.safetensors
      └── README.md

Họ có thể upload model lên Hugging Face để người khác tải về.

3. "Model trên Hugging Face" nghĩa là gì?

Ví dụ:

Qwen/Qwen3-VL-4B-Instruct

Thường có dạng:

<organization>/<model>

Trong đó:

Qwen

là tổ chức phát triển.

Qwen3-VL-4B-Instruct

là tên model.

Mày có thể tưởng tượng Hugging Face giống một kho model khổng lồ:

                 HUGGING FACE
                      │
        ┌─────────────┼─────────────┐
        │             │             │
       Qwen          Meta          Google
        │             │             │
     Qwen3          Llama         Gemma
        │
    Qwen3-VL
4. Transformer là gì?

Đây mới là phần quan trọng.

Transformer là một kiến trúc mạng neural network được giới thiệu trong paper:

Attention Is All You Need (2017)

Nó trở thành nền tảng cho rất nhiều mô hình AI hiện đại.

Ví dụ:

ChatGPT
Gemini
Claude
Qwen
Llama
DeepSeek

nhiều model ngôn ngữ hiện đại đều sử dụng các kiến trúc dựa trên Transformer hoặc các biến thể của nó.

Transformer làm gì?

Ví dụ mày đưa:

"Tôi đang học AI"

Model không hiểu trực tiếp câu này như con người.

Nó biến câu thành các đơn vị gọi là token:

"Tôi"   "đang"   "học"   "AI"
 ↓       ↓        ↓       ↓
token   token    token   token

Sau đó các token được biến thành vector số.

token
  ↓
embedding
  ↓
vector
  ↓
Transformer
  ↓
prediction

Một thành phần cực kỳ quan trọng của Transformer là:

Attention

Nó giúp model xác định:

"Từ nào liên quan đến từ nào?"

Ví dụ:

Tôi đặt laptop lên bàn vì nó rất nặng.

Model cần xác định:

"nó" → laptop

Attention giúp model học được những quan hệ kiểu này.

5. Qwen3-VL-4B-Instruct là gì?

Đây là một model cụ thể.

Tách tên ra:

Qwen3-VL-4B-Instruct
│    │  │   │
│    │  │   └── phiên bản instruction
│    │  └────── khoảng 4B parameters
│    └───────── Vision-Language
└────────────── thế hệ Qwen3
Qwen3

Dòng model Qwen thế hệ 3.

VL

Vision-Language

Có khả năng xử lý hình ảnh + ngôn ngữ, tùy model/cấu hình cụ thể.

Ví dụ:

Ảnh
 ↓
Qwen3-VL
 ↓
"Trong ảnh có một người đang đứng cạnh xe máy."

Không chỉ text:

Text → Model → Text

mà có thể:

Image ─┐
        ├──→ Model ──→ Text
Text ───┘
4B

4B = khoảng 4 billion parameters, tức khoảng 4 tỷ tham số.

Parameter là các con số mà model học được trong quá trình training.

Không phải:

4B = 4 tỷ từ.

Mà là khoảng:

4 tỷ giá trị tham số của neural network.

6. Instruct nghĩa là gì?

Ví dụ model gốc:

Qwen3-...

và model:

Qwen3-...-Instruct

"Instruct" thường chỉ phiên bản đã được tối ưu để làm theo instruction của người dùng.

Ví dụ:

User:
Tóm tắt nội dung ảnh này.

Model:
Đây là ảnh chụp một...

Thay vì chỉ đơn thuần dự đoán token tiếp theo.

Nên khi làm chatbot/assistant, phiên bản Instruct thường là loại rất đáng chú ý.

7. Safetensors là gì?

Đây là chỗ nhiều người mới học AI hay nhầm.

.safetensors không phải model.

Nó là định dạng file chứa tensor/weights của model.

Ví dụ:

Qwen3-VL-4B-Instruct
        │
        ├── config.json
        ├── tokenizer.json
        └── model.safetensors

Trong file model.safetensors có rất nhiều số.

Ví dụ tưởng tượng:

weight_1 = 0.1837
weight_2 = -0.7291
weight_3 = 1.3821
...

Hàng tỷ giá trị như vậy tạo nên weights/parameters của model.

8. Tại sao lại có safetensors?

Trước đây model thường được lưu bằng các định dạng như:

.pth
.pt
.bin

Trong hệ sinh thái PyTorch, một số cách serialize cũ có thể liên quan đến Python pickle, vốn có rủi ro khi tải dữ liệu không đáng tin cậy.

safetensors được thiết kế như một định dạng tensor an toàn hơn và hiệu quả hơn cho việc lưu/truyền weights.

Ví dụ:

model.safetensors

không có nghĩa:

đây là một loại AI mới.

Mà chỉ là:

đây là cái hộp chứa trọng số của AI.

9. Quan hệ giữa Qwen và safetensors

Cái này cực kỳ quan trọng.

Đừng nghĩ:

Qwen ≠ safetensors

Chúng là hai thứ khác nhau.

Ví dụ:

Qwen3-VL-4B-Instruct
        │
        │ model
        ↓
┌───────────────────────┐
│      Weights          │
│                       │
│  ████████████████     │
│  ████████████████     │
│  ████████████████     │
└───────────────────────┘
        │
        ↓
model.safetensors

Qwen3-VL-4B-Instruct = model.

safetensors = cách lưu weights của model đó.

10. Local model vs API model

Đây là phần tao nghĩ sẽ giúp mày hiểu câu:

"Mấy anh chị cứ kêu gọi API Gemini"

Có 2 cách rất khác nhau để sử dụng AI.

Cách 1 — Chạy model local

Ví dụ mày tải:

Qwen3-VL-4B-Instruct

về máy.

Internet
   │
   │ download
   ↓
┌────────────────────┐
│      PC của mày    │
│                    │
│ Qwen3-VL-4B        │
│        ↓           │
│      GPU           │
│        ↓           │
│    kết quả         │
└────────────────────┘

Lúc này model chạy trên máy của mày.

Ví dụ Python:

from transformers import ...

hoặc thông qua các framework inference khác.

GPU của mày phải gánh việc tính toán.

11. Cách 2 — Gọi API

Ví dụ Gemini.

Mày không tải model Gemini về máy.

Thay vào đó:

                 INTERNET
                    │
                    │ request
                    ↓
┌──────────────┐       ┌──────────────────┐
│   PC của mày │ ────→ │ Google Gemini    │
│              │       │ Server           │
│ Python code  │ ←──── │ AI model         │
└──────────────┘       └──────────────────┘
                    response

Code của mày gửi:

"Phân tích ảnh này"

Google xử lý.

Sau đó trả:

"Trong ảnh có..."

về cho chương trình.

Đó chính là:

Gọi API Gemini.

12. API thực chất là gì?

API = Application Programming Interface.

Tên nghe rất hàn lâm nhưng hiểu đơn giản:

API là một cách để chương trình này yêu cầu chương trình/hệ thống khác làm một việc và trả kết quả về.

Ví dụ đời thường:

Mày
 │
 │ gọi món
 ↓
Nhân viên
 │
 │ gửi yêu cầu
 ↓
Nhà bếp
 │
 │ nấu
 ↓
Nhân viên
 │
 │ trả món
 ↓
Mày

API cũng tương tự:

Python
 │
 │ request
 ↓
API
 │
 ↓
AI Server
 │
 │ xử lý
 ↓
API
 │
 │ response
 ↓
Python
13. Request và Response

Hai từ này mày sẽ gặp liên tục khi làm API.

Request

Yêu cầu gửi đi.

Ví dụ:

POST /generate

với dữ liệu:

{
  "prompt": "Explain Transformer"
}
Response

Kết quả server trả về:

{
  "answer": "Transformer is a neural network architecture..."
}

Nói ngắn:

REQUEST  →  Server
REQUEST  ←  Response
14. Endpoint là gì?

API thường có những địa chỉ cụ thể gọi là endpoint.

Ví dụ tưởng tượng:

https://api.example.com/v1/chat

Đây là một endpoint.

Có thể có:

/v1/chat
/v1/embeddings
/v1/images

Mỗi endpoint cung cấp một chức năng khác nhau.

15. GET và POST là gì?

Mày sẽ gặp hai cái này rất nhiều.

GET

Thường dùng để lấy dữ liệu.

GET /users

Ý nghĩa:

Cho tôi danh sách users.

POST

Thường dùng để gửi dữ liệu lên server để xử lý/tạo thứ gì đó.

Ví dụ AI:

POST /chat

Body:

{
    "prompt": "Hello"
}

Server xử lý rồi trả response.

16. API Key là gì?

Đây chắc chắn là thứ mày sẽ gặp nếu đang thực tập.

API Key = một loại credential/token dùng để xác thực request của mày.

Ví dụ:

Python
   │
   │ API Key: sk-xxxx
   ↓
OpenAI API

Server nhìn vào key để biết:

Request này thuộc về tài khoản/project nào?

Từ đó có thể áp dụng quyền hạn, hạn mức, billing...

Cực kỳ quan trọng

Đừng đưa API key lên GitHub.

Ví dụ:

API_KEY = "sk-xxxxxxxxxxxx"

rồi:

git push

💀

Key có thể bị lộ.

Thường dùng:

.env

Ví dụ:

GEMINI_API_KEY=xxxxxxxx

Python:

import os

api_key = os.getenv("GEMINI_API_KEY")
17. REST API là gì?

REST API là một kiểu thiết kế API rất phổ biến.

Ví dụ một hệ thống quản lý sinh viên:

GET    /students
GET    /students/123
POST   /students
PUT    /students/123
DELETE /students/123

Hiểu kiểu đơn giản:

Method	Ý nghĩa
GET	Lấy
POST	Tạo/gửi
PUT/PATCH	Cập nhật
DELETE	Xóa

Khi anh chị bảo:

"Em biết REST API không?"

thì họ thường đang hỏi:

Em có hiểu cách các hệ thống giao tiếp với nhau qua HTTP/API không?

18. HTTP là gì?

API trên Internet thường sử dụng HTTP/HTTPS.

Ví dụ:

Python
  │
  │ HTTPS request
  ↓
https://api.google.com/...
  │
  ↓
Google server
  │
  │ HTTPS response
  ↓
Python

Một số status code mày chắc chắn sẽ gặp:

Code	Ý nghĩa
200	Thành công
201	Tạo thành công
400	Request sai
401	Chưa xác thực / API key sai
403	Không có quyền
404	Không tìm thấy
429	Gửi quá nhiều request
500	Server lỗi

Ví dụ mày từng gặp:

401 Unauthorized
Incorrect API key

thì nghĩa cơ bản là:

Server nhận request nhưng không chấp nhận credential/API key của mày.

19. JSON là gì?

API thường trao đổi dữ liệu bằng JSON.

Ví dụ:

{
  "name": "Cuong",
  "age": 20,
  "major": "Computer Science"
}

Nó giống dictionary trong Python:

{
    "name": "Cuong",
    "age": 20,
    "major": "Computer Science"
}

Nên Python làm việc với REST API rất tiện.

20. requests trong Python là gì?

requests là thư viện Python giúp gửi HTTP request.

Ví dụ:

import requests

response = requests.get(
    "https://api.example.com/users"
)

print(response.status_code)
print(response.json())

Tức là:

Python
   │
   │ requests.get()
   ↓
HTTP GET
   ↓
API Server
   ↓
JSON Response
   ↓
Python
21. Vậy "gọi API Gemini" thực tế là gì?

Ví dụ mày có một app:

Ứng dụng của mày
       │
       │ "Hãy tóm tắt đoạn văn này"
       ↓
   Gemini API
       │
       ↓
   Gemini model
       │
       ↓
"Đoạn văn nói về..."
       │
       ↓
Ứng dụng của mày

Mày không cần:

❌ tải model
❌ tải weights
❌ cần GPU mạnh để chạy model
❌ tự host model

Đổi lại:

✅ cần Internet
✅ cần API key
✅ thường có giới hạn/chi phí tùy dịch vụ
22. Local model và API — so sánh cực nhanh
	Local Qwen	Gemini API
Model chạy ở đâu?	Máy mày	Server Google
Có tải model về?	Có	Không
Cần GPU?	Thường có lợi/rất quan trọng tùy model	Không cần GPU local
Internet	Có thể không cần sau khi tải	Cần
API key	Không nhất thiết	Có
Dữ liệu gửi server	Có thể không	Có, tùy cách sử dụng
Tự kiểm soát model	Cao	Thấp hơn
Dễ bắt đầu	Tương đối phức tạp	Khá dễ
23. Một khái niệm nữa: Transformers library

Đừng nhầm:

Transformer và Transformers.

Transformer

Là kiến trúc AI.

Transformers

Là một thư viện Python rất phổ biến của Hugging Face.

Ví dụ:

from transformers import AutoTokenizer
from transformers import AutoModel

Nó giúp mày:

Python
   ↓
Transformers library
   ↓
Load model
   ↓
Qwen / Llama / Gemma / ...

Nên khi mày thấy:

pip install transformers

thì đây là thư viện, không phải kiến trúc Transformer.

24. Còn PyTorch là gì?

Cũng rất hay gặp.

PyTorch là một framework machine learning/deep learning.

Có thể hình dung:

                    AI application
                          │
                 Transformers
                          │
                       PyTorch
                          │
                       CUDA
                          │
                         GPU

Ví dụ Qwen có thể được chạy thông qua hệ sinh thái:

Qwen model
    ↓
Transformers
    ↓
PyTorch
    ↓
CUDA
    ↓
NVIDIA GPU

Đây cũng liên quan trực tiếp đến cái mày từng gặp:

Torch not compiled with CUDA enabled

Nó có nghĩa đại khái:

PyTorch hiện tại của mày không có/không sử dụng được CUDA backend, nên model không chạy được trên GPU bằng CUDA.

25. Ghép tất cả lại

Đây là sơ đồ mày nên lưu lại trong đầu:

                    HUGGING FACE
                         │
               ┌─────────┴─────────┐
               │                   │
            Models              Libraries
               │                   │
        Qwen3-VL-4B          Transformers
               │                   │
               │                   │
               └────────┬──────────┘
                        │
                     Model
                        │
                 ┌──────┴──────┐
                 │             │
             Weights       Tokenizer
                 │
          .safetensors
                 │
                 ↓
              PyTorch
                 │
               CUDA
                 │
                GPU

Còn nếu không chạy local:

Your Python program
       │
       │ HTTPS
       ↓
   Gemini API
       │
       ↓
Google's server
       │
       ↓
 Gemini model
       │
       ↓
    Response
       │
       ↓
Your Python program
26. Và đây là "bản đồ thuật ngữ" mày nên học

Nếu mày đang bước vào AI/Data/AI Engineer, tao khuyên hiểu theo thứ tự này:

LEVEL 1 — Internet/API
│
├── HTTP / HTTPS
├── Request / Response
├── GET / POST
├── Endpoint
├── JSON
├── Status code
├── API Key
└── REST API

LEVEL 2 — Python AI ecosystem
│
├── NumPy
├── Pandas
├── PyTorch
├── CUDA
└── Transformers

LEVEL 3 — LLM
│
├── Token
├── Tokenizer
├── Embedding
├── Parameter
├── Weight
├── Context window
├── Attention
├── Transformer
├── Inference
└── Fine-tuning

LEVEL 4 — Model
│
├── Qwen
├── Llama
├── Gemma
├── DeepSeek
├── Qwen3-VL
└── 4B / 7B / 14B / ...

LEVEL 5 — Model files
│
├── safetensors
├── config.json
├── tokenizer.json
├── checkpoint
├── quantization
├── FP32
├── FP16
├── BF16
└── INT8 / INT4

LEVEL 6 — Deployment
│
├── Local inference
├── API inference
├── vLLM
├── Ollama
├── Docker
├── GPU serving
└── Cloud inference

Nếu mày nắm được 6 tầng này thì lúc mấy anh chị nói "load model Hugging Face", "safetensors", "inference", "call Gemini API", "REST API", "endpoint", "token", "4B model", "CUDA"... mày sẽ bắt đầu hiểu họ đang nói về tầng nào, thay vì nghe toàn từ lạ.



*********************************************************************************************************************************

1\. trọng số là gì ?

2. Làm sao code tự gửi yêu cầu lên server của gg được ?
3. Spaces trên hugging face là gì ?
4. Libraries là gì ?
5. tiện trình bày sơ về llama và gemma luôn đi
6. 6\. Ý nghĩa của tham số của neural network là gì, nó thật sự nói lên điều gì ?
7. framework inference là gì ?
8. json là gì, tại sao gửi đi và trả về lại qua json. Post là gì, thuộc ngôn ngữ nào



Được. Tao giải thích theo kiểu **“hiểu bản chất trước, thuật ngữ sau”**, vì nếu chỉ học thuộc định nghĩa thì vài hôm nữa lại rối tiếp.

---

# 1. Trọng số (weight) là gì?

Đây là khái niệm **cốt lõi nhất của neural network**.

Hãy bắt đầu bằng một neuron cực đơn giản:

```text
x1 ──× w1 ──┐
x2 ──× w2 ──┼──→ cộng lại → activation → y
x3 ──× w3 ──┘
```

Nó thực hiện gần giống:

```text
y = activation(x1*w1 + x2*w2 + x3*w3 + b)
```

Trong đó:

* `x1, x2, x3`: dữ liệu đầu vào
* `w1, w2, w3`: **trọng số (weights)**
* `b`: bias
* `y`: đầu ra

Ví dụ:

```text
x1 = 10
x2 = 2

w1 = 0.8
w2 = -0.3
```

thì:

```text
10 × 0.8 + 2 × (-0.3)
= 8 - 0.6
= 7.4
```

### Vậy trọng số có ý nghĩa gì?

Nó thể hiện **mức độ và chiều hướng mà một tín hiệu đầu vào ảnh hưởng đến đầu ra của một phép tính mà neuron đang thực hiện**.

Ví dụ:

```text
w = 5
```

→ tín hiệu đó có ảnh hưởng mạnh theo chiều dương.

```text
w = -5
```

→ ảnh hưởng mạnh theo chiều ngược lại.

```text
w ≈ 0
```

→ ảnh hưởng rất ít trong phép tính đó.

Nhưng **đừng hiểu rằng mỗi weight có một ý nghĩa con người đọc được**, kiểu:

> `weight #123456 = mức độ quan trọng của từ "con mèo"`

Không đơn giản như vậy.

Trong một model lớn, hàng tỷ weights **kết hợp với nhau** để biểu diễn các pattern phức tạp.

---

# 2. Vậy model "học" bằng cách nào?

Đây mới là phần thú vị.

Ban đầu model có weights gần như chưa hữu ích:

```text
w1 = 0.12
w2 = -0.73
w3 = 0.04
...
```

Nó nhìn dữ liệu training:

```text
Input:
"Thủ đô của Việt Nam là"

Expected:
"Hà Nội"
```

Model dự đoán:

```text
"TP.HCM"
```

→ sai.

Training algorithm tính **loss** để đo mức sai.

Sau đó dùng **backpropagation + optimizer** để điều chỉnh weights.

```text
Input
  ↓
Neural network
  ↓
Prediction
  ↓
So với đáp án
  ↓
Loss
  ↓
Backpropagation
  ↓
Điều chỉnh weights
  ↓
Lặp lại
```

Hàng triệu/hàng tỷ/lần lặp sau:

```text
weights
   ↓
được điều chỉnh
   ↓
model nhận ra pattern tốt hơn
```

Vì vậy có thể hiểu rất đơn giản:

> **Training = tìm một bộ weights giúp model thực hiện nhiệm vụ tốt.**

---

# 3. Thế 4B parameters thực sự là gì?

Khi người ta nói:

> Qwen3-VL-4B

thì `4B` đại khái là:

> **khoảng 4 tỷ parameter.**

Parameter chủ yếu là các giá trị mà mạng neural **học được trong quá trình training**, trong đó weights là thành phần rất lớn.

Ví dụ cực kỳ đơn giản:

```text
Model nhỏ:

w1 = 0.12
w2 = -0.83
w3 = 1.72
w4 = 0.004
...
```

Model 4B:

```text
~4.000.000.000 parameter
```

Không phải:

```text
4 tỷ từ
4 tỷ kiến thức
4 tỷ câu
```

Mà là:

> **4 tỷ con số tham gia vào các phép tính của neural network.**

---

# 4. Nhưng 4 tỷ con số "nói lên" điều gì?

Nó nói lên **quy mô của mô hình**, chứ không trực tiếp nói:

> "Model thông minh gấp 4 lần model 1B."

Không có chuyện đó.

Nhiều parameter hơn **có thể** cho phép model biểu diễn những pattern phức tạp hơn, nhưng chất lượng còn phụ thuộc vào:

* dữ liệu training
* kiến trúc
* cách training
* fine-tuning
* tokenizer
* context
* dữ liệu instruction
* chất lượng tối ưu hóa...

Cho nên:

```text
14B ≠ chắc chắn tốt hơn 7B trong mọi nhiệm vụ
```

---

# 5. Làm sao code tự gửi yêu cầu lên server Google?

Cái này thực ra **không thần kỳ gì cả** =)))

Máy tính của mày vốn đã có khả năng giao tiếp Internet bằng HTTP/HTTPS.

Ví dụ:

```text
Python
  │
  │ HTTPS request
  ↓
Google server
  │
  │ xử lý
  ↓
HTTP response
  │
  ↓
Python
```

Code có thể dùng thư viện HTTP hoặc SDK của Google.

Ví dụ khái niệm:

```python
response = requests.post(
    "https://api.google.com/...",
    headers={
        "Authorization": "..."
    },
    json={
        "prompt": "Xin chào Gemini"
    }
)
```

Python thực hiện request.

Hệ điều hành + thư viện mạng sẽ tạo kết nối Internet:

```text
Python
 ↓
requests
 ↓
HTTP/HTTPS
 ↓
Internet
 ↓
Google server
```

Server Google nhận request → xác thực API key → xử lý → trả response.

---

# 6. Tại sao Google cho phép máy mày gọi server của họ?

Vì Google **công khai một API**.

Họ quy định:

> Nếu chương trình của mày gửi request đúng format và có credential hợp lệ, server của Google sẽ xử lý.

Giống như một cửa:

```text
                GOOGLE SERVER

             ┌───────────────────┐
Request ───→ │   Gemini API      │
             │                   │
             │ API key hợp lệ?   │
             │ Format đúng?      │
             └─────────┬─────────┘
                       │
                       ↓
                    Gemini
                       │
                       ↓
                   Response
```

Đó chính là **API contract**:

> Google quy định mày phải gửi cái gì, gửi ở đâu, bằng phương thức nào, và họ sẽ trả về cái gì.

---

# 7. Spaces trên Hugging Face là gì?

**Spaces** là nơi người ta **deploy ứng dụng/demo AI** trên Hugging Face.

Ví dụ thay vì:

> "Tôi có model nhận diện ảnh."

người ta có thể làm thành giao diện:

```text
┌──────────────────────────────┐
│       AI IMAGE DEMO          │
│                              │
│  [ Upload image ]            │
│                              │
│       ┌──────────────┐       │
│       │     ảnh      │       │
│       └──────────────┘       │
│                              │
│       [ Analyze ]            │
│                              │
│ Result: cat                  │
└──────────────────────────────┘
```

và đưa nó lên **Hugging Face Spaces**.

Người khác chỉ cần mở web → dùng.

Spaces thường được xây bằng những framework như:

* Gradio
* Streamlit
* Docker

Nên:

```text
Hugging Face Model
       │
       ↓
   Python code
       │
       ↓
     Space
       │
       ↓
  Web interface
```

### Phân biệt

**Models**

```text
"Đây là model."
```

**Datasets**

```text
"Đây là dữ liệu."
```

**Spaces**

```text
"Đây là ứng dụng/demo dùng model."
```

---

# 8. Libraries là gì?

**Library = thư viện phần mềm.**

Nói đơn giản:

> Một đống code được người khác viết sẵn để mày sử dụng lại.

Ví dụ mày muốn tính toán ma trận.

Tự viết:

```text
hàng trăm dòng code
```

Thay vào đó dùng:

```python
import numpy
```

và:

```python
numpy.array(...)
```

---

## Ví dụ đời thường

Không có library:

```text
Mày muốn làm xe
↓
Tự chế động cơ
Tự chế bánh
Tự chế hộp số
...
```

Có library:

```text
Người khác đã làm động cơ
↓
Mày lấy ra dùng
```

Trong AI:

| Library      | Dùng để                          |
| ------------ | -------------------------------- |
| NumPy        | tính toán mảng/số                |
| Pandas       | xử lý dữ liệu                    |
| OpenCV       | xử lý ảnh/video                  |
| PyTorch      | deep learning                    |
| Transformers | load/use nhiều model Transformer |
| Requests     | HTTP request                     |

---

# 9. Framework khác Library như thế nào?

Đây là một cặp cũng rất dễ nhầm.

### Library

Mày **gọi nó**.

```python
import requests

requests.get(...)
```

```text
MÀY
 ↓
Library
```

### Framework

Framework thường cung cấp **khung hoạt động lớn hơn**, và chương trình của mày chạy bên trong framework đó.

Ví dụ:

```text
Application
      ↓
Framework
      ↓
các thành phần xử lý
```

Một cách nhớ đơn giản:

> **Library: mày gọi nó.**
> **Framework: nó định hình cách ứng dụng của mày chạy.**

Ranh giới thực tế đôi khi không hoàn toàn tuyệt đối, nhưng cách hiểu này đủ tốt để bắt đầu.

---

# 10. Framework inference là gì?

**Inference = cho model chạy để tạo dự đoán/kết quả.**

Ví dụ:

```text
Training:

Data
 ↓
Model
 ↓
điều chỉnh weights
 ↓
Model đã học
```

Sau khi training xong:

```text
Inference:

Input
 ↓
Model
 ↓
Output
```

Ví dụ:

```text
Ảnh con mèo
      ↓
Qwen3-VL
      ↓
"Đây là một con mèo."
```

---

## Framework inference

Là phần mềm/framework giúp **đưa model vào trạng thái chạy inference một cách hiệu quả**.

Ví dụ có:

* vLLM
* TensorRT-LLM
* llama.cpp
* Ollama
* Transformers

Chúng giải quyết những vấn đề như:

```text
load model
↓
load weights
↓
đưa model lên GPU
↓
nhận input
↓
tokenize
↓
model inference
↓
generate output
```

Một số framework tập trung mạnh vào **tốc độ, memory usage và serving nhiều request**.

Ví dụ:

```text
User 1 ─┐
User 2 ─┤
User 3 ─┼──→ inference server → GPU → Model
User 4 ─┘
```

---

# 11. JSON là gì?

JSON = **JavaScript Object Notation**.

Đừng bị cái tên JavaScript đánh lừa.

JSON hiện nay được sử dụng cực kỳ rộng rãi để **trao đổi dữ liệu giữa các hệ thống**.

Ví dụ:

```json
{
  "name": "Cuong",
  "age": 20,
  "major": "Computer Science"
}
```

Có thể hiểu:

```text
key       value
 ↓          ↓
"name" → "Cuong"
"age"  → 20
```

---

# 12. Tại sao API hay dùng JSON?

Vì JSON:

### 1. Dễ đọc

Con người nhìn vẫn hiểu:

```json
{
  "name": "Cuong",
  "age": 20
}
```

### 2. Máy dễ parse

Python:

```python
data = response.json()
```

JavaScript:

```javascript
JSON.parse(...)
```

Java, Go, C#, PHP... đều xử lý JSON được.

### 3. Không phụ thuộc một ngôn ngữ

Ví dụ:

```text
Python
   ↓
 JSON
   ↓
Java
```

hoặc:

```text
JavaScript
   ↓
 JSON
   ↓
Python
```

Hai chương trình khác ngôn ngữ vẫn trao đổi dữ liệu được.

---

# 13. Tại sao không gửi thẳng Python object?

Vì server có thể không viết bằng Python.

Ví dụ:

```text
App của mày:
Python

Google server:
C++ / Go / Java / Python / ...
```

Nếu mày gửi một object Python kiểu:

```python
Student(...)
```

thì Google server không nhất thiết biết object đó là gì.

Nhưng nếu gửi:

```json
{
  "name": "Cuong",
  "age": 20
}
```

thì gần như ngôn ngữ nào cũng hiểu được.

Đó là một trong những lý do JSON cực kỳ phổ biến.

---

# 14. POST là gì? Thuộc ngôn ngữ nào?

**POST không thuộc Python, Java, JavaScript hay ngôn ngữ lập trình nào cả.**

Đây là một **HTTP method**.

HTTP có các method phổ biến:

```text
GET
POST
PUT
PATCH
DELETE
```

Ví dụ:

```text
GET /students
```

thường mang ý nghĩa:

> Lấy danh sách sinh viên.

Còn:

```text
POST /students
```

thường mang ý nghĩa:

> Gửi dữ liệu để tạo một sinh viên mới.

---

# 15. POST trong API AI

Đây là ví dụ rất điển hình:

```text
POST /generate
```

Mày gửi:

```json
{
  "prompt": "Giải thích Transformer"
}
```

Server xử lý.

Trả:

```json
{
  "response": "Transformer là..."
}
```

Toàn bộ quá trình:

```text
                    INTERNET

Python
  │
  │ POST
  │
  │ /generate
  │
  │ {
  │   "prompt": "Giải thích Transformer"
  │ }
  ↓
┌─────────────────────┐
│     AI SERVER       │
│                     │
│   nhận request      │
│        ↓            │
│      Model          │
│        ↓            │
│   generate output   │
└──────────┬──────────┘
           │
           │ HTTP Response
           ↓
{
  "response": "Transformer là..."
}
```

---

# 16. Vậy `requests.post()` nghĩa là gì?

Ví dụ:

```python
import requests

response = requests.post(
    "https://example.com/api",
    json={
        "prompt": "Hello"
    }
)
```

Đọc bằng tiếng Việt:

> **Dùng thư viện `requests` của Python để gửi một HTTP POST request đến endpoint `/api`, trong đó body chứa dữ liệu JSON.**

Tách từng phần:

```text
requests
   ↓
Python library

.post()
   ↓
HTTP POST method

"https://..."
   ↓
API endpoint

json={...}
   ↓
dữ liệu gửi lên
```

---

# 17. Một ví dụ cực sát với "gọi Gemini API"

Về mặt khái niệm:

```python
response = client.models.generate_content(
    model="gemini-...",
    contents="Giải thích Transformer"
)
```

Mày gọi một **SDK/client library**.

Bên dưới SDK sẽ lo phần giao tiếp HTTP/API với server.

Nó đại khái làm:

```text
Code của mày
    ↓
Gemini SDK
    ↓
HTTP request
    ↓
Google API
    ↓
Gemini model
    ↓
HTTP response
    ↓
Gemini SDK
    ↓
Code của mày
```

Cho nên khi anh chị nói:

> **"Gọi API Gemini"**

thì đừng nghĩ có một cái hàm thần bí tên là Gemini chạy trên laptop.

Hãy nghĩ:

> **"Code của mình đang gửi HTTP request tới dịch vụ AI của Google, yêu cầu model Gemini xử lý dữ liệu và nhận kết quả trả về."**

---

# 18. Llama và Gemma là gì?

Hai cái này cũng là **họ/dòng model**, giống như Qwen.

## Llama

Meta phát triển dòng **Llama**.

Ví dụ:

```text
Llama
 ├── Llama 3
 ├── Llama 3.1
 ├── Llama 3.2
 └── các biến thể khác
```

Llama là một trong những dòng **open-weight language models** nổi tiếng.

Ví dụ khi mày thấy:

```text
Llama 3.1 8B
```

thì:

```text
Llama      → dòng model
3.1        → phiên bản
8B         → khoảng 8 tỷ parameters
```

Có thể tải một số model Llama về và chạy local, tùy license, phần cứng và model cụ thể.

---

# 19. Gemma là gì?

**Gemma** là dòng model do Google phát triển.

Có thể xem:

```text
Google
  │
  └── Gemma
       ├── Gemma
       ├── Gemma 2
       ├── Gemma 3
       └── các biến thể
```

Gemma hướng tới các model có thể được **sử dụng/deploy bởi developer và researcher**, với nhiều kích thước model khác nhau.

Đặc biệt:

> **Gemma model ≠ Gemini API**

Đây là chỗ rất dễ nhầm.

---

# 20. Gemini vs Gemma

Nhớ bảng này:

|                   | Gemini                                      | Gemma                               |
| ----------------- | ------------------------------------------- | ----------------------------------- |
| Google            | ✅                                           | ✅                                   |
| Dòng sản phẩm     | AI model/service                            | Model family                        |
| API cloud         | ✅                                           | Có thể có tùy dịch vụ/hạ tầng       |
| Chạy local        | Không theo cách thông thường của Gemini API | Một số model có thể                 |
| Tải weights       | Không phải cách sử dụng Gemini thông thường | Có các model/weights được phát hành |
| Dùng Hugging Face | Có thể có tài nguyên liên quan              | Rất phổ biến                        |

Nói cực ngắn:

```text
Gemini
→ "Tôi gọi AI của Google qua dịch vụ/API."

Gemma
→ "Tôi lấy một model thuộc dòng Gemma để sử dụng/deploy theo cách được hỗ trợ."
```

---

# 21. Qwen – Llama – Gemma nằm cùng "nhóm" nào?

Ở mức khái quát:

```text
             LANGUAGE / MULTIMODAL MODELS
                       │
       ┌───────────────┼────────────────┐
       │               │                │
      Qwen            Llama            Gemma
       │               │                │
   Alibaba/Qwen       Meta            Google
```

Ví dụ:

```text
Qwen3-VL-4B-Instruct
Llama 3.1 8B
Gemma 3 4B
```

đều là **tên model/model family cụ thể**, chứ không phải:

```text
Transformer
API
safetensors
Hugging Face
```

Những cái kia là **những tầng khái niệm khác nhau**.

---

# 22. Cuối cùng, mày hãy nhớ cái sơ đồ này

Nếu mày đang học AI thì đây là sơ đồ quan trọng nhất:

```text
                         AI
                          │
              ┌───────────┴───────────┐
              │                       │
          MODEL LOCAL             MODEL API
              │                       │
       ┌──────┴──────┐          ┌─────┴─────┐
       │             │          │           │
      Qwen          Llama      Gemini      ...
       │             │
       └──────┬──────┘
              │
         Transformer
              │
       ┌──────┴──────┐
       │             │
    Parameters     Tokenizer
       │
     Weights
       │
 .safetensors
       │
       ↓
    PyTorch
       ↓
     CUDA
       ↓
      GPU
```

Còn Hugging Face:

```text
                 HUGGING FACE
                       │
          ┌────────────┼─────────────┐
          │            │             │
        Models      Datasets       Spaces
          │                          │
      Qwen/Llama                AI demo/app
          │
     .safetensors
```

Và API:

```text
Your program
     │
     │ HTTP Request
     │
     │ POST
     │ JSON
     │ API Key
     ↓
  API Endpoint
     ↓
  AI Server
     ↓
    Model
     ↓
 HTTP Response
     ↓
    JSON
     ↓
Your program
```

**Nếu chỉ cần chốt 10 từ khóa của bài này thì nhớ:**

> **Weight = con số model học được**
> **Parameter = các giá trị học được của model**
> **Transformer = kiến trúc neural network**
> **Qwen/Llama/Gemma = các dòng model**
> **safetensors = định dạng lưu weights**
> **Hugging Face = hệ sinh thái/kho model, dataset, app**
> **Spaces = nơi deploy demo/app AI**
> **Library = code viết sẵn để mình dùng**
> **Inference = cho model chạy để tạo output**
> **API = cách chương trình của mình giao tiếp với dịch vụ bên ngoài**

Đến đây nếu mày muốn **thực sự hiểu sâu**, bước tiếp theo nên là học **token → tokenizer → embedding → attention → Transformer → LLM generate từng token như thế nào**. Đó là đoạn nối trực tiếp từ "4 tỷ con số" sang "tại sao nó có thể đọc ảnh và trả lời tao".



Để dễ hình dung và không bị rối, chúng ta sẽ bẻ nhỏ toàn bộ hệ thống `QC_OCR` thành một dây chuyền sản xuất gồm **7 bước rõ ràng**.

Mỗi bước tương ứng với một file code mà mày đã tạo trong thư mục `app/`. Cứ đi từng bước một như sau:

---

### BƯỚC 1: Đưa tài liệu vào hệ thống

* **File liên quan:** `telegram_bot.py` (hoặc bỏ trực tiếp vào thư mục `data/input/`).
* **Làm gì:** Nhân viên chụp ảnh form (JPG/PNG) hoặc quét file PDF rồi ném lên Telegram Bot của công ty (hoặc copy vào thư mục input). Hệ thống nhận được file và tạo một mã đơn hàng (`job_id`).

### BƯỚC 2: Tách trang PDF (Nếu file là PDF)

* **File liên quan:** `app/pdf_processor.py`
* **Làm gì:**
* Nếu là ảnh JPG/PNG $\rightarrow$ Bỏ qua bước này.
* Nếu là file PDF dày 5 trang $\rightarrow$ Dùng thư viện `pymupdf` cắt thành 5 file ảnh PNG riêng biệt rồi lưu vào thư mục `data/pages/`.



### BƯỚC 3: Tiền xử lý và Cắt vùng cần đọc (ROI)

* **File liên quan:** `app/image_preprocess.py` và `app/form_template.py`
* **Làm gì:**
* Làm nét ảnh, xoay thẳng ảnh nếu bị nghiêng (`image_preprocess.py`).
* Dựa vào khung chuẩn (`form_template.py`), hệ thống biết chính xác "ô tên khách hàng", "ô tổng tiền" nằm ở tọa độ nào trên ảnh để cắt ra (crop) thành các mảnh nhỏ lưu vào `data/crops/`. *Việc này giúp AI không bị nhiễu bởi các phần thừa xung quanh.*



### BƯỚC 4: Gọi AI Local đọc chữ (OCR)

* **File liên quan:** `app/qwen_ocr.py`
* **Làm gì:**
* Code Python đọc file ảnh crop ở Bước 3, biến thành dạng dữ liệu bytes.
* Gửi request vào **Local API** (đang chạy ngầm trong máy công ty qua Ollama / Qwen3-VL).
* Mô hình Qwen3-VL tự động "nhìn" ảnh và trả về một chuỗi **Raw OCR JSON** chứa thông tin bóc tách được.



### BƯỚC 5: Kiểm tra độ chính xác (Validator)

* **File liên quan:** `app/validator.py`
* **Làm gì:**
* Kiểm tra xem JSON trả về có đúng định dạng không, các trường dữ liệu quan trọng (như mã số thuế, tổng tiền) có bị thiếu hay không.
* Nếu điểm tin cậy (confidence) cao $\rightarrow$ Cho đi tiếp.
* Nếu thấp hoặc nghi ngờ sai sót $\rightarrow$ Đẩy qua bước 6.



### BƯỚC 6: Human-in-the-loop (Sửa lỗi qua Telegram)

* **File liên quan:** `app/telegram_bot.py`
* **Làm gì:**
* Nếu AI đọc nhầm hoặc không chắc chắn, bot sẽ gửi ảnh kèm thông tin lỗi vào nhóm chat Telegram của nhân viên.
* Nhân viên bấm nút sửa trực tiếp trên điện thoại/máy tính $\rightarrow$ Hệ thống cập nhật lại thành **Validated JSON**.



### BƯỚC 7: Điền dữ liệu vào Excel

* **File liên quan:** `app/mapper.py` và `app/excel_writer.py`
* **Làm gì:**
* Dùng `mapping.json` để dịch các trường dữ liệu từ JSON sang đúng các cột trong mẫu Excel của công ty (Sheet 05).
* `excel_writer.py` tiến hành ghi đè/tạo file Excel hoàn chỉnh và lưu vào `data/output/`.



---

### Tóm lại bằng một câu:

Nhân viên ném file vào $\rightarrow$ Code tự cắt ảnh $\rightarrow$ Gọi Local API (Qwen3-VL) đọc chữ $\rightarrow$ Kiểm tra lỗi $\rightarrow$ Tự động điền ra file Excel.

Mọi thứ chạy tự động và khép kín hoàn toàn trong máy công ty! Dễ hình dung hơn chưa mày?