# WEAVERSE 프로젝트

<img src="https://github.com/nathanLYJ/NathanLYJ/blob/main/attackment/weaverse로고.PNG" width="400" height="200" alt="로고">

WEAVERSE는 온라인 영상 교육 플랫폼을 구현하기 위한 프로젝트입니다.

## 팀 구성

| 이름 | 유원길 | 임홍광 | 이유정 | 유연우 |
|------|--------|--------|--------|--------|
| GitHub | <a href="https://github.com/nathanLYJ"><img src="https://github.com/nathanLYJ/NathanLYJ/blob/main/attackment/%EC%9C%A0%EC%9B%90%EA%B8%B8.jpg" width="100" height="100" alt="유원길"></a> |<a href="https://github.com/AlbertImKr"><img src="https://github.com/nathanLYJ/NathanLYJ/blob/main/attackment/%EC%9E%84%ED%99%8D%EA%B4%91.jpg" width="100" height="100" alt="임홍광"></a> | <a href="https://github.com/devnproyj22"><img src="https://github.com/nathanLYJ/NathanLYJ/blob/main/attackment/%EC%9D%B4%EC%9C%A0%EC%A0%95.jpg" width="100" height="100" alt="이유정"></a> | <a href="https://github.com/Yoo117"><img src="https://github.com/nathanLYJ/NathanLYJ/blob/main/attackment/%EC%9C%A0%EC%97%B0%EC%9A%B0.jpg" width="100" height="100" alt="유연우"></a>|
| 역할 | 팀원 | 팀원 | 팀장 | 팀원 |
| 담당 | 인증,인가 | Course,Mission | 사용자,이미지,비디오 | payments, Cart, Order |

## 기술 스택

### 언어
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

### 프레임워크 & 주요 라이브러리
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![dj-rest-auth](https://img.shields.io/badge/dj--rest--auth-6.0.0-blue?style=for-the-badge)
![django-allauth](https://img.shields.io/badge/django--allauth-65.0.2-yellow?style=for-the-badge)

### 데이터베이스
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

### 클라우드 & 스토리지
![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![S3](https://img.shields.io/badge/S3-569A31?style=for-the-badge&logo=amazon-s3&logoColor=white)

### 문서화
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![drf-spectacular](https://img.shields.io/badge/drf--spectacular-0.27.2-green?style=for-the-badge)

### 테스팅
![Pytest](https://img.shields.io/badge/pytest-8.3.3-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

### 기타 주요 라이브러리
- django-cors-headers
- django-filter
- Pillow (이미지 처리)
- moviepy, ffmpeg-python (비디오 처리)
- gunicorn (WSGI HTTP 서버)

## API 구조

### 인증 (Auth)

| 엔드포인트                  | 메서드   | 설명                                            | 인증 필요 |
|---------------------------|--------|-----------------------------------------------|---------|
| `/api/login/`             | `POST` | 사용자가 로그인하고 토큰을 발급받습니다.                   | 불필요    |
| `/api/logout/`            | `POST` | 사용자가 로그아웃합니다.                              | 필요     |
| `/api/refresh/`           | `POST` | 사용자가 Refresh 토큰으로 새 토큰을 발급받습니다.          | 불필요    |
| `/api/social-login/google/`| `GET`  | 사용자를 Google 로그인 페이지로 리다이렉트합니다.           | 불필요    |
| `/api/social-login/google/`| `POST` | Google 인증 후 사용자 정보를 받아 로그인 또는 회원가입 처리합니다. | 불필요    |

### 사용자 (CustomUser)

#### 수강생 (Student)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/accounts/student/register/` | `POST` | 새로운 수강생을 생성합니다. (회원가입) | 불필요 |
| `/api/accounts/students/` | `GET` | 수강생 목록을 조회합니다. | 필요 |
| `/api/accounts/students/{id}/` | `GET` | 수강생 정보를 조회합니다. | 필요 |
| `/api/accounts/students/{id}/` | `PUT` | 수강생 정보를 수정합니다. | 필요 |
| `/api/accounts/students/{id}/` | `PATCH` | 수강생 정보를 부분 수정합니다. | 필요 |
| `/api/accounts/students/{id}/` | `DELETE` | 수강생이 탈퇴합니다. (소프트 삭제) | 필요 |

#### 강사 (Tutor)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/accounts/tutors/` | `GET` | 강사 목록을 조회합니다. | 필요 |
| `/api/accounts/tutors/{id}/` | `GET` | 강사 정보를 조회합니다. | 필요 |
| `/api/accounts/tutors/{id}/` | `PUT` | 강사 정보를 수정합니다. | 필요 |
| `/api/accounts/tutors/{id}/` | `PATCH` | 강사 정보를 부분 수정합니다. | 필요 |
| `/api/accounts/tutors/{id}/` | `DELETE` | 강사를 삭제합니다. (소프트 삭제) | 필요 |

#### 공통

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/accounts/password/reset/` | `POST` | 비밀번호를 재설정합니다. | 필요 |

### 이미지 (Image)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/materials/images/upload/` | `POST` | 새로운 이미지를 업로드합니다. | 필요 |
| `/api/materials/images/` | `GET` | 모든 이미지를 가져옵니다. | 필요 |
| `/api/materials/images/` | `POST` | 새로운 이미지를 생성합니다. | 필요 |
| `/api/materials/images/{id}/` | `GET` | 특정 이미지를 조회합니다. | 필요 |
| `/api/materials/images/{id}/` | `PUT` | 특정 이미지를 수정합니다. | 필요 |
| `/api/materials/images/{id}/` | `DELETE` | 특정 이미지를 삭제합니다. | 필요 |

### 비디오 (Video)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/materials/videos/upload/` | `POST` | 새로운 비디오를 업로드합니다. | 필요 |
| `/api/materials/videos/` | `GET` | 모든 비디오를 가져옵니다. | 필요 |
| `/api/materials/videos/` | `POST` | 새로운 비디오를 생성합니다. | 필요 |
| `/api/materials/videos/{id}/` | `GET` | 특정 비디오를 조회합니다. | 필요 |
| `/api/materials/videos/{id}/` | `PUT` | 특정 비디오를 수정합니다. | 필요 |
| `/api/materials/videos/{id}/` | `DELETE` | 특정 비디오를 삭제합니다. | 필요 |

### 비디오 이벤트 데이터 (Video Event Data)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/materials/video-event-data/` | `POST` | 새로운 비디오 이벤트 데이터를 생성합니다. | 필요 |
| `/api/materials/users/{user_id}/videos/{video_id}/watch-history/` | `GET` | 특정 사용자의 특정 비디오 시청 기록을 조회합니다. | 필요 |

### 과목 (Course)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/courses/courses/` | `GET` | 모든 과목 목록을 조회합니다. | 불필요 |
| `/api/courses/courses/` | `POST` | 새로운 과목을 생성합니다. | 필요 (staff) |
| `/api/courses/courses/{id}/` | `GET` | 특정 과목 정보를 조회합니다. | 불필요 |
| `/api/courses/courses/{id}/` | `PUT` | 과목 정보를 수정합니다. | 필요 (staff) |
| `/api/courses/courses/{id}/` | `PATCH` | 과목 정보를 부분 수정합니다. | 필요 (staff) |
| `/api/courses/courses/{id}/` | `DELETE` | 특정 과목을 삭제합니다. | 필요 (staff) |

참고:
- 검색 기능: `title`, `short_description`, `description` 필드로 검색 가능
- 필터링: `category`, `skill_level` 필드로 필터링 가능
- 정렬: `created_at`, `price` 필드로 정렬 가능

### 커리큘럼 (Curriculum)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/courses/curriculums/` | `GET` | 모든 커리큘럼 목록을 조회합니다. | 불필요 |
| `/api/courses/curriculums/` | `POST` | 새로운 커리큘럼을 생성합니다. | 필요 (staff) |
| `/api/courses/curriculums/{id}/` | `GET` | 특정 커리큘럼 정보를 조회합니다. | 불필요 |
| `/api/courses/curriculums/{id}/` | `PUT` | 커리큘럼 정보를 수정합니다. | 필요 (staff) |
| `/api/courses/curriculums/{id}/` | `PATCH` | 커리큘럼 정보를 부분 수정합니다. | 필요 (staff) |
| `/api/courses/curriculums/{id}/` | `DELETE` | 특정 커리큘럼을 삭제합니다. | 필요 (staff) |

참고:
- 검색 기능: `title`, `description` 필드로 검색 가능
- 필터링: `category`, `skill_level` 필드로 필터링 가능
- 정렬: `created_at`, `price` 필드로 정렬 가능

### 장바구니 (Cart)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/payments/cart/` | `GET` | 사용자의 장바구니를 조회합니다. | 필요 |
| `/api/payments/cart/` | `POST` | 장바구니에 상품을 추가합니다. | 필요 |
| `/api/payments/cart/{cart_item_id}/` | `GET` | 특정 장바구니 아이템을 조회합니다. | 필요 |
| `/api/payments/cart/{cart_item_id}/` | `DELETE` | 장바구니에서 특정 상품을 삭제합니다. | 필요 |

### 주문 (Order)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/payments/orders/` | `GET` | 사용자의 진행 중인 주문을 조회합니다. | 필요 |
| `/api/payments/orders/` | `POST` | 새로운 주문을 생성합니다. | 필요 |

### 청구 주소 (Billing Address)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/payments/billing-addresses/` | `GET` | 사용자의 모든 청구 주소를 조회합니다. | 필요 |
| `/api/payments/billing-addresses/` | `POST` | 새로운 청구 주소를 생성합니다. | 필요 |
| `/api/payments/billing-addresses/{billing_address_id}/` | `GET` | 특정 청구 주소를 조회합니다. | 필요 |
| `/api/payments/billing-addresses/{billing_address_id}/` | `PUT` | 특정 청구 주소를 수정합니다. | 필요 |
| `/api/payments/billing-addresses/{billing_address_id}/` | `DELETE` | 특정 청구 주소를 삭제합니다. | 필요 |

### 결제 (Payment)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/payments/payments/` | `POST` | 결제를 생성하고 카카오페이 결제를 요청합니다. | 필요 |
| `/api/payments/payments/` | `GET` | 카카오페이 결제 결과를 처리합니다. | 필요 |
| `/api/payments/payments/{order_id}/cancel/` | `DELETE` | 결제를 취소하고 환불을 처리합니다. | 필요 |

### 영수증 (Receipt)

| 엔드포인트 | 메서드 | 설명 | 인증 필요 |
|------------|--------|------|----------|
| `/api/payments/receipts/` | `GET` | 사용자의 모든 영수증 목록을 조회합니다. | 필요 |
| `/api/payments/receipts/{payment_id}/` | `GET` | 특정 결제에 대한 상세 영수증 정보를 조회합니다. | 필요 |

## ERD **수정 필요**

![erd](assets/images/erd.png)

## WBS **수정 필요**

### 프로젝트 초기 설정 및 환경 구축

![week0](assets/images/week0.png)

### 1주차 기능 구현 **수정 필요**

![week1](assets/images/week1.png)

### 2주차 기능 구현 **수정 필요**

![week2](assets/images/week2.png)

### 최종 검토 및 문서화 **수정 필요**

![week3](assets/images/week3.png)

## 문제 해결 
### ACCOUNTS

### MATERIALS

### JWTAUTH

### COURSES

### PAYMENTS
