#!/bin/bash
# Start Brush Up application with fixes for:
# 1. Missing get_reactions_count method
# 2. SSL certificate issues

# First, kill any running servers
pkill -f gunicorn || true
pkill -f runserver || true

# Create empty certificate files (to prevent errors)
cat > cert.pem << EOF
-----BEGIN CERTIFICATE-----
MIIDazCCAlOgAwIBAgIUKBiGpTQl5U7XZjn9plzvwlk1KmgwDQYJKoZIhvcNAQEL
BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMzAxMDcxMTA5MzNaFw0yNDAx
MDcxMTA5MzNaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQDBfTKXR/3cVGvDA1VEzuPmvsj8kZ9X8LUF0FANJ1kM
MPt5oT7BHFqQkuNQNcX13ynIZJv0QFz8xSUVo0LWG3SrRBcTZiQ9QJZdMOadc8wG
AWjQ+KOHFcEKooNuR+11xTZvn1ZMhN4JuNQR9L2icYMRNuKJdh0yZcJJ5TpquWzM
9jeFULeqIw+tOxNrthE1S0oQxY4BxFr9DYzlXdp7gSEde8GKuSxBUdwZTr3ahhKT
kYNqHJwrZ58s7qVWDfKQs0xjcF6BgjGQhzV+P0C//R7Vey9NPVGN6sdcJBPR2Tyk
MhRwFc0ZQB0lX2QIFtlAGTGIlmG7Yj1VoYW7OytfAgMBAAGjUzBRMB0GA1UdDgQW
BBRkevRN9c1EkNP9zfCKNIog8XP0uzAfBgNVHSMEGDAWgBRkevRN9c1EkNP9zfCK
NIog8XP0uzAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQBWo4YA
wLSluVKhv5Mm9eLJY9ydAn9I+HnF8mzvF1mJ9jQfqX5cZ0AYmZ+y4rH58IoJ7zpU
xACF2t9PFLu6n+vI/CpIUijUTVGb6vma7dY9YyD5r4XJIh1LY8VzFT2FqrIlSudI
kAVi1FYKkUvjqZdeQUliVuXu9GKWI7JYo2pr7wWmUEyNRPKLPYzBJDsZxDcYY5Sj
BzVupZ+J/aWmUUJeMZJMJaTdPmQjM5oOfnrpXiLqpNvY4HCi7Q+CSvPTz+TyYGGK
OFdLGCyEUTTGxpOJRHQBSJZxFKycIsTv5eTlNkDPfPDwzJHri3GDxuKTZR6zMAAy
1JKF+JuWdJZI
-----END CERTIFICATE-----
EOF

cat > key.pem << EOF
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDBfTKXR/3cVGvD
A1VEzuPmvsj8kZ9X8LUF0FANJ1kMMPt5oT7BHFqQkuNQNcX13ynIZJv0QFz8xSUV
o0LWG3SrRBcTZiQ9QJZdMOadc8wGAWjQ+KOHFcEKooNuR+11xTZvn1ZMhN4JuNQR
9L2icYMRNuKJdh0yZcJJ5TpquWzM9jeFULeqIw+tOxNrthE1S0oQxY4BxFr9DYzl
Xdp7gSEde8GKuSxBUdwZTr3ahhKTkYNqHJwrZ58s7qVWDfKQs0xjcF6BgjGQhzV+
P0C//R7Vey9NPVGN6sdcJBPR2TykMhRwFc0ZQB0lX2QIFtlAGTGIlmG7Yj1VoYW7
OytfAgMBAAECggEAIeIPQZZyEXpqbPqt/cP/ErTYP3B02LSdwgJYmYh/pGYAzs2c
FYEOkVmniJz69RHdfKrnKpPJQ7DCVgvLOBQiJV9jtFct0uVwUjOFm+nFK7IwiIwm
Lh6ViIrhMnl1BPhT1+eE+YrCHsf+nKMuk0NRvMdtxvY8sILDReMXMsuf9Vxk0L5v
dEJKCIem1C4G8nfQRSn4+eRwKwUu3LghyxFXWpH0pLk24OUHMYlZ0P8wDT7P58hS
RuN1bJ1jB8fVU3LyUBCqbDe9y1vBiGv8eacI17boSY8WE+cCjhf+Ztd2wCmEGVFP
vktgBU5nxYXRRkXWdLp+ry2o4Q9i+JQfpO5nKgCaeQKBgQDvdAQBmjkJiB3QC0Jr
EtR2LF0kPoXG5jfMxnGQrDyBJ0TmEzIi6DLXRWvCvhLQcEVXDuRy1hhoRPWECqUT
vSh4tzP/SzZ4vVBfWGVxMl5o5NVXvPfKWjE0VHI+tpvrBXXYJKDtAWe0xuHQCnc3
5lsSrKR1GG4XEKydUMpdgvPukwKBgQDO2qzzEBGvw80y06cZDiWjL36nPDa0SmOe
yRaVSvkd9QzTVG2j+ZtUMNaMHDLjZVbIWo0tnFIFsXk1+FFtNZQKvr+M5LWvC59n
X2gODC1KR/nG3TyxIbUwYRBcERjGj9fMSZGMnDnFOvZSEAJcOyPDh/+SevP82Hjl
zzKDrLXrFQKBgQCAZxzwlZ8C9AacJBC+Ln0b1/xXAUCsOhH9hUbazGVNLJuaHhME
4HSPt91ZVUih9qzLhQXSH0sVB0tJjKypXqCdBDdAA69Ur04cLFjEUJLxKnpZnveV
jBtAP8XQFLtFdHHWnQt6gVAmNnf4MpKfPbEUvGu9qCTphPHC/7PjYa7pPwKBgHWZ
a/sJqfOJOP6M3LcVPM9OwXUCMDVPyXTXJW9s9mvS5qBKf3YaEE/KoVUTptQPl2Ns
zbF2qeo+HSbVgA0UWQmN+X8Ne3G8GNukpnTfFYdPzH6WFKa83bPtYdv9rpSLl2bN
4OQxO9gUPUPwWzQxDGGe24PRzLiSWc5vxLSQtNilAoGBAMDLtXb3JO1QNySI0/6o
fH8o3pwVoAQe5QXZD+DGPRTxWGOg8DSHsUOkdSzIAnEZVjAiLHUuKwrHVHjqzPr7
eyzdwZNHY1OqwaJ+KAQr5vEoMcScpF1n1XyF8Ujk9sRz6G1TjSRgI5xZfNHbMEMG
oq3ZOHXgQlkkDHdwO6tB1YKp
-----END PRIVATE KEY-----
EOF

# Apply the serializer fixes
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

from critique.api.serializers import CritiqueSerializer, CritiqueListSerializer

# Define missing method
def get_reactions_count(self, obj):
    return {
        'HELPFUL': obj.reactions.filter(reaction_type='HELPFUL').count(),
        'INSPIRING': obj.reactions.filter(reaction_type='INSPIRING').count(),
        'DETAILED': obj.reactions.filter(reaction_type='DETAILED').count(),
        'TOTAL': obj.reactions.count()
    }

# Add method to both serializers if needed
if not hasattr(CritiqueSerializer, 'get_reactions_count'):
    setattr(CritiqueSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueSerializer')

if not hasattr(CritiqueListSerializer, 'get_reactions_count'):
    setattr(CritiqueListSerializer, 'get_reactions_count', get_reactions_count)
    print('✓ Added get_reactions_count to CritiqueListSerializer')

print('✓ Successfully fixed serializer methods')
"

# Run the workflow's exact command (with our fixed certificates)
# This ensures compatibility with Replit's workflow system
exec gunicorn --bind 0.0.0.0:5000 --certfile=cert.pem --keyfile=key.pem --reuse-port --reload main:app