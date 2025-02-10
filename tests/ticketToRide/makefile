CC = gcc

SOURCES = src/main.c ../../client/src/api.c
OBJS = ${SOURCES:.c=.o}

all: build clean run

build: $(OBJS)
	@$(CC) -o dist/programm $(OBJS)

%.o: %.c
	@$(CC) -c $< -o $@

clean: ${OBJS}
	@rm -rf ${OBJS}

run: ./dist/programm
	@./dist/programm

runLeak: dist/programm
	@valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes --verbose --log-file=valgrind-out.txt ./dist/programm