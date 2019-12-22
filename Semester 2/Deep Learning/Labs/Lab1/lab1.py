import time
import torch
from argparse import ArgumentParser


def exercise1():
    mat_size = 13
    two_rows = [1,6,11]
    # Generate all ones matrix
    mat = torch.ones((mat_size, mat_size))
    # Add the 2s
    mat[two_rows, :] = torch.full((3,mat_size), 2)
    mat[:, two_rows] = torch.full((mat_size,3), 2)
    # Add the 3s
    mat[3:5,3:5] = mat[3:5,8:10] = torch.full((2,2), 3)
    mat[8:10,3:5] = mat[8:10,8:10] = torch.full((2,2), 3)
    print(mat)


def exercise2():
    torch.manual_seed(1)
    mat_size = 20
    mat = torch.empty((mat_size, mat_size))
    mat.normal_()
    diag = torch.diag(torch.arange(1,mat_size+1, dtype=torch.float32))
    mat = torch.inverse(mat) @ diag @ mat
    print(torch.eig(mat))


def exercise3():
    mat_size = 5000
    # Set start time
    start_time = time.perf_counter()
    # Generate matrices
    A = torch.empty((mat_size,mat_size))
    A.normal_()
    B = torch.empty((mat_size,mat_size))
    B.normal_()
    # Multiply matrices
    C = A @ B
    # Measure end time
    end_time = time.perf_counter()
    print(f'The operations took {end_time - start_time} seconds.')
    print(f'There were {mat_size**3} floating point products.')


def exercise4():
    def mul_row(mat):
        res = mat.clone()
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                res[i,j] *= (i + 1)
        return res

    def mul_row_fast(mat):
        res = mat.clone()
        mul = torch.arange(1,mat.shape[0]+1, dtype=torch.float32).view(-1,1)
        res = torch.mul(mul, res)
        return res

    mat = torch.full((1000,400), 2)
    start_time = time.perf_counter()
    simple_op = mul_row(mat)
    end_time = time.perf_counter()
    print('Time for simple operations:', end_time - start_time)
    start_time = time.perf_counter()
    fast_op = mul_row_fast(mat)
    end_time = time.perf_counter()
    print('Time for fast operations:', end_time - start_time)


def run_exercise(exercise):
    globals()[f'exercise{exercise}']()


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--exercise', type=int, default=1,
        help='choose exercise to run')
    args = argparser.parse_args()

    run_exercise(args.exercise)
