# python 业务镜像模版
FROM 路径/python_base:3.6.8

# 应用名
ARG APP_NAME  
# 执行的Binary名字
ARG APP_BIN 
# 环境名字
ARG ENV_TYPE
# 需要COPY打到镜像的内容
ARG ARCHIVE

ENV APP_NAME=${APP_NAME} APP_BIN=${APP_BIN} ENV_TYPE=${ENV_TYPE}

ADD requirements.txt /appruntime/python/

COPY start.sh /appruntime/python/

RUN yum install git -y && \
    mkdir -p /appruntime/python/${APP_NAME} && \
    cd /appruntime/python/${APP_NAME} && \
    mv /appruntime/python/requirements /appruntime/python/${APP_NAME}/ && \
    pip install --no-cache-dir -r requirements -i https://mirrors.aliyun.com/pypi/simple/

COPY ${ARCHIVE} /appruntime/python/${APP_NAME}








