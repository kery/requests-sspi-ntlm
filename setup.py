from setuptools import setup

setup(name="requests_sspi_ntlm",
      version="0.0.1",
      author="Kery Wu",
      author_email="kery.wu@qq.com",
      description="HTTP NTLM authentication using SSPI module for requests library",
      license="BSD",
      keywords="ntlm requests",
      url="https://github.com/kery/requests-sspi-ntlm",
      packages=["requests_sspi_ntlm"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
      ]
)
