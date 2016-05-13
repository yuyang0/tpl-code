DEBUG ?= 1

uname_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')

CC = gcc
AR = ar
RANLIB = ranlib

ifeq ($(DEBUG), 1)
    CFLAGS := -g -Wall -fPIC -std=gnu99 -DDEBUG
else
    CFLAGS := -O2 -fPIC -std=gnu99 -DNDEBUG
endif

EXTRA_INC_PATH = -I../common

EXE_FILE = exe

OBJS = aa.o bb.o
SOURCES = $(OBJS:.o=.c)

all: $(EXE_FILE)

$(EXE_FILE): $(OBJS)
	$(CC) -o $@ $^ -lrt -rdynamic -lpthread

# Header file deps (use make dep to generate this)
-include Makefile.dep

dep Makefile.dep:
	$(CC) -MM $(SOURCES) > Makefile.dep

.PHONY: dep

%.o:%.c
	$(CC) -c $(CFLAGS) $(CPPFLAGS) $< -o $@ $(EXTRA_INC_PATH)


install: all
	@if [ -d $(INSTDIR) ]; \
	then \
	cp myapp $(INSTDIR);\
	chmod a+x $(INSTDIR)/$(EXE_FILE);\
	chmod og-w $(INSTDIR)/$(EXE_FILE);\
	echo “Installed in $(INSTDIR)“;\
	else \
	echo “Sorry, $(INSTDIR) does not exist”;\
	fi

.PHONY: clean
clean:
	rm -f *.o $(EXE_FILE)
