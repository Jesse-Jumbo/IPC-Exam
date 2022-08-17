CC=gcc

JSON_C_DIR=/usr/local
LDFLAGS += -L$(JSON_C_DIR)/lib -ljson-c -lzmq
CFLAGS += -I$(JSON_C_DIR)/include/json-c

client: Consumer.c
	$(CC) Consumer.c -o Consumer $(LDFLAGS) $(CFLAGS)
clean:
	$(RM) *.o
