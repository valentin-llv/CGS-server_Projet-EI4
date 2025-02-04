CC = gcc

SOURCES = $(wildcard src/*.c)
OBJS = ${SOURCES:.c=.o}

all: build clean runLeak

build: $(OBJS)
	@$(CC) -o dist/client $(OBJS)

%.o: %.c
	@$(CC) -c $< -o $@

clean: ${OBJS}
	@rm -rf ${OBJS}

run: ./dist/client
	@./dist/client

runLeak: dist/programm
	@valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes --verbose --log-file=valgrind-out.txt ./dist/client