from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

def send_mail_by_domain(subject, message, recipient_email):
    """도메인(@gmail.com, @naver.com, @daum.net)에 따라 다른 SMTP 계정을 사용하여 메일 전송"""
    if not recipient_email or '@' not in recipient_email:
        raise ValueError("잘못된 이메일 주소입니다.")

    domain = recipient_email.split('@')[-1].lower()
    domain_config = settings.EMAIL_CONFIGS.get(domain, None)

    # 도메인 설정이 없는 경우(=허용 안 함) → 에러 or 기본 SMTP 사용
    if not domain_config:
        # 1) 거부하는 경우
        # raise ValueError(f"허용되지 않은 도메인: {domain}")

        # 2) fallback SMTP 사용
        domain_config = settings.DEFAULT_EMAIL_CONFIG
    print(domain_config)
    # SMTP 백엔드를 동적으로 생성
    email_backend = EmailBackend(
        host=domain_config['HOST'],
        port=domain_config['PORT'],
        username=domain_config['USER'],
        password=domain_config['PASSWORD'],
        use_tls=domain_config.get('USE_TLS', False),
        use_ssl=domain_config.get('USE_SSL', False),
    )
    print(email_backend)
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=domain_config['USER'],  # 보통 SMTP 계정과 동일
        to=[recipient_email],
        connection=email_backend
    )
    print(email)
    email.send(fail_silently=False)
    print("메일 전송 완료!")