from django.conf import settings


def get_client_ip(request):
    """사용자의 IP 주소

    X-Forwarded-For의 앞쪽 값은 클라이언트가 임의로 넣을 수 있으므로,
    신뢰하는 프록시(NUM_PROXIES개)가 덧붙인 뒤쪽 값을 사용한다.
    """
    num_proxies = getattr(settings, "NUM_PROXIES", 1)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if num_proxies and x_forwarded_for:
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        return ips[max(len(ips) - num_proxies, 0)]
    return request.META.get("REMOTE_ADDR")
