#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <zmq.h>
#include "json-c/json.h"

typedef struct MATRIX {
    double** mat;
    int row;
    int col;
} t_matrix;

// declaration of functions
struct json_object* load_env_parameters(const char*);
struct json_object* Worker(char*);
t_matrix* initialize_matrix(int, int);
t_matrix* get_matrix_from_json_object(struct json_object*, char*);
t_matrix* conv2d(t_matrix*, t_matrix*);
void refill_image_in_json(struct json_object*, t_matrix*);

int main() {
    // load env parameters
    struct json_object* env = load_env_parameters("./SystemParameters.json");
    struct json_object* socket_producer_consumer = NULL;
    struct json_object* socket_consumer_collector = NULL;
    socket_producer_consumer =  json_object_object_get(env, "socket_producer_consumer");
    socket_consumer_collector = json_object_object_get(env, "socket_consumer_collector");

    // connection settings
    printf("[Consumer] Connecting to Server...\n");
    void* context = zmq_ctx_new();
    void* socket_producer = zmq_socket(context, ZMQ_PUSH);
    void* socket_collector = zmq_socket(context, ZMQ_PULL);
    zmq_connect(socket_producer, json_object_get_string(socket_producer_consumer));
    zmq_connect(socket_collector, json_object_get_string(socket_consumer_collector));
    
    // infinite loop (worker)
    while(1) {
        struct json_object* work;
        void* buffer = (void*)malloc(35000 * 35000 * sizeof(char));

        // receive task from producer
        printf("[Consumer] Waiting for new work!\n");
        size_t s = zmq_recv(socket_producer, buffer, 35000 * 35000, 0);

        // calculate conv2d
        work = Worker((char*) buffer);
        // send message to result collector
        const char* msg = json_object_to_json_string(work);
        zmq_send(socket_collector, msg, (int) strlen(msg)/2 , 0);
        
        free(buffer);
    }

    zmq_close(socket_producer);
    zmq_close(socket_collector);
    zmq_ctx_destroy(context);
}

struct json_object* Worker(char* buf) {
    // parse received buffer
    struct json_object* rjobj;
    rjobj = json_tokener_parse(buf);
    t_matrix* m_mask = get_matrix_from_json_object(rjobj, "mask");
    t_matrix* m_matrix = get_matrix_from_json_object(rjobj, "image");
    // conv2d
    t_matrix* m_ans = conv2d(m_matrix, m_mask);
    // replace  "matrix" into the convolved matrix
    refill_image_in_json(rjobj, m_ans);
    return rjobj;
}

t_matrix* initialize_matrix(int col, int row) {
    // initialize matrix with size (col, row)
    t_matrix* mat = malloc(sizeof(t_matrix));
    mat->col = col;
    mat->row = row;
    mat->mat = malloc(sizeof(double*) * col);
    for (int i = 0; i < col; i++) {
        mat->mat[i] = calloc(sizeof(double), row);
    }

    return mat;
}

t_matrix* get_matrix_from_json_object(struct json_object* jobj, char* key) {

    struct json_object* matrix = json_object_object_get(jobj, key);

    /* initialize matrix */
    t_matrix* mat;
    // matrix is a 2d array
    int col = json_object_array_length(matrix);
    // get row length from the first row 0
    int row = json_object_array_length(
        json_object_array_get_idx(matrix, 0)
    );
    mat = initialize_matrix(col, row);
    printf("[Consumer] %s size = %d %d\n", key, mat->col, mat->row);

    /* retreive matrix from json */
    for (int i = 0; i < mat->col; i++) {
        struct json_object* row = json_object_array_get_idx(matrix, i);
        for (int j = 0; j < mat->row; j++) {
            mat->mat[i][j] = json_object_get_double(
                json_object_array_get_idx(row, j)
            );
        }
    }

    return mat;
}

t_matrix* conv2d (t_matrix* Q, t_matrix* M) {
    t_matrix* A = initialize_matrix((Q->col-M->col+1), (Q->row-M->row+1));

    // convolution (time domain)
    // you can implement the convolution using FFT to replace this slower one

    for (int i = 0; i < A->col; i++) {
    for (int j = 0; j < A->row; j++) {
        for (int k = 0; k < M->col; k++) {
        for (int l = 0; l < M->row; l++) {
            // Mask [k][l]
            // Q [i+k][j+l]
            if ((i+k < Q->col) && (j+l < Q->row))
                A->mat[i][j] += (M->mat[k][l] * Q->mat[i+k][j+l])
            else // border
                A->mat[i][j] += 0.;
        }
        }
    }
    }

    printf("[Consumer] finish conv2d\n");
    return A;
}

void refill_image_in_json(struct json_object* jobj, t_matrix* ans) {
    // we are going to replace the "image" in the received object
    // into conv2d-ed image
    // The new json object will be the msg buffer and send to the collector
    struct json_object* matrix = json_object_object_get(jobj, "image");
    // clear question matrix
    matrix = json_object_new_array(); 

    // fill conv2d-ed matrix into json object
    for (int i = 0; i < ans->col; i++) {
        struct json_object* narr = json_object_new_array();
        for (int j = 0; j < ans->row; j++) {
            struct json_object* val = json_object_new_double(ans->mat[i][j]);
            json_object_array_add(narr, val);
        }
        json_object_array_add(matrix, narr);
    }
}

struct json_object* load_env_parameters(const char* path) {
    struct json_object* env = NULL;
    int fd;

    env = json_object_from_file(path);
    return env;
}
