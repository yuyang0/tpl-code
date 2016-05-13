DEBUG ?= 1

all:build

build: build-agent

build-agent:
	@mkdir -p ./bin
	make -C ./agent/ DEBUG=$(DEBUG)
	@rm -f ./bin/agent
	@cp -f ./agent/agent ./bin/

clean:
	@rm -rf ./bin/agent
	make -C ./agent/ clean
