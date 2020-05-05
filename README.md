# Job Recruit crawling_project
- 손주현, 이진주
- [Jobplanet](https://www.jobplanet.co.kr/)
- [Wanted](https://www.wanted.com.kr/)

### 프로젝트 주제
- 잡플래닛의 데이터사이언스 관련 채용공고와 해당 기업리뷰 수집
- Flask로 웹 페이지에 구현하고, slack 메시지 보내기

### 주제 선정 이유
- 데이터사이언스 분야로 취업하는데 도움이 되는 정보를 편리하게 수집하기 위해서
- 채용공고와 기업리뷰를 한눈에 볼 수 있다면, 채용공고를 볼 때 기업의 문화를 동시에 파악할 수 있어 지원할 회사를 선택할 때 도움을 얻을 수 있다.

### 데이터
- 채용공고
    - 링크, 회사이름, 산업분야, 공고제목, 채용기간, 채용공고내용
- 기업리뷰
    - 링크, 리뷰내용(장점, 단점, 바라는 점), 전체리뷰통계, 총 리뷰수, 리뷰작성자 직군
    
### 코드 작성
- 채용공고 크롤링 : crawling_recruit.py 모듈 내에 JobPlanet Class
    - 채용공고 수집, mongodb로 저장하는 함수
- 기업 리뷰 크롤링 : 
  - 기업 리뷰 수집, mongodb로 저장하는 함수 
- Flask, slack chatbot 

