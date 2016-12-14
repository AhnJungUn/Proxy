환경:

Windows 10 환경에서 Python 2.7.11 버젼으로 작성된 코드입니다.


실행: 

1) 업로드 된 파일들을 모두 같은 디렉토리에 위치.

2) cert_gen.sh 파일을 실행시켜 root certificates 생성. 이 후 역시 위와 같은 디렉토리에 저장. 

3) 만들어진 root 인증서를 신뢰할 수 있는 루트 인증기관 안에 등록

4) C:\ 에 인증서 저장을 위한 Certificates 폴더 생성

5) 브라우져 옵션 설정에서 프록시 서버 설정을, 127.0.0.1 : 8080 으로 맞춤

6) 관리자 모드로 proxy.py 를 실행 

 만약 Data Change 옵션을 원한다면 "proxy.py 8080 before after" 의 형식으로 커맨드 입력
 
 그렇지 않으면 "proxy.py 8080" 으로 커맨드 입력

 

 