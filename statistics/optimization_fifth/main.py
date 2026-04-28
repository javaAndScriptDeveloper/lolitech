from _pydecimal import Decimal
from scipy.stats import f, t

m = 0
d = 0
N = 15

x1_min = -2
x1_max = 3
x2_min = 0
x2_max = 10
x3_min = -4
x3_max = 8

x01 = (x1_max - x1_min) / 2
x02 = (x2_max - x2_min) / 2
x03 = (x3_max - x3_min) / 2
delta_x1 = x1_max - x01
delta_x2 = x2_max - x02
delta_x3 = x3_max - x03
y_min = 200 + int((x1_min + x2_min + x3_min) / 3)
y_max = 200 + int((x1_max + x2_max + x3_max) / 3)

def sqrt(element):
    from math import sqrt
    return sqrt ( element )


def fab(element):
    from math import fabs
    return fabs ( element )

correct_input = False
while not correct_input: #making sure the input  is correct
    try:
        m = int(input("Enter number of reiteration: "))
        p = float(input("Enter confidence probability: "))
        correct_input = True
    except ValueError:
        pass

#starts cycle where the main code performs
correct = False
while not correct:
    try:
        array = [#initial array
            [-1, -1, -1, +1, +1, +1, -1, +1, +1, +1],
            [-1, -1, +1, +1, -1, -1, +1, +1, +1, +1],
            [-1, +1, -1, -1, +1, -1, +1, +1, +1, +1],
            [-1, +1, +1, -1, -1, +1, -1, +1, +1, +1],
            [+1, -1, -1, -1, -1, +1, +1, +1, +1, +1],
            [+1, -1, +1, -1, +1, -1, -1, +1, +1, +1],
            [+1, +1, -1, +1, -1, -1, -1, +1, +1, +1],
            [+1, +1, +1, +1, +1, +1, +1, +1, +1, +1],
            [-1.215, 0, 0, 0, 0, 0, 0, 1.4623, 0, 0],
            [+1.215, 0, 0, 0, 0, 0, 0, 1.4623, 0, 0],
            [0, -1.215, 0, 0, 0, 0, 0, 0, 1.4623, 0],
            [0, +1.215, 0, 0, 0, 0, 0, 0, 1.4623, 0],
            [0, 0, -1.215, 0, 0, 0, 0, 0, 0, 1.4623],
            [0, 0, +1.215, 0, 0, 0, 0, 0, 0, 1.4623],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]



        class Critical_values: #class which contains static method to calculate criterios values
            @staticmethod
            def get_cohren_value(size_of_selections, qty_of_selections, significance):
                size_of_selections += 1
                partResult1 = significance / (size_of_selections - 1)
                params = [partResult1, qty_of_selections, (size_of_selections - 1 - 1) * qty_of_selections]
                fisher = f.isf(*params)
                result = fisher / (fisher + (size_of_selections - 1 - 1))
                return Decimal(result).quantize(Decimal('.0001')).__float__()

            @staticmethod
            def get_student_value(f3, significance):
                return Decimal(abs(t.ppf(significance / 2, f3))).quantize(Decimal('.0001')).__float__()

            @staticmethod
            def get_fisher_value(f3, f4, significance):
                return Decimal(abs(f.isf(significance, f4, f3))).quantize(Decimal('.0001')).__float__()

        def x(l1, l2, l3):
            x_1 = l1 * delta_x1 + x01
            x_2 = l2 * delta_x2 + x02
            x_3 = l3 * delta_x3 + x03
            return [x_1, x_2, x_3]


        def generate_matrix(): #matrix with Y
            from random import randrange
            matrix_with_y = [[randrange(y_min, y_max) for y in range(m)] for x in range(N)]
            return matrix_with_y


        def find_average(lst, orientation):
            average = []
            if orientation == 1:
                for rows in range(len(lst)):
                    average.append(sum(lst[rows]) / len(lst[rows]))
            else:
                for column in range(len(lst[0])):
                    number_lst = []
                    for rows in range(len(lst)):
                        number_lst.append(lst[rows][column])
                    average.append(sum(number_lst) / len(number_lst))
            return average


        def count(first , second):
            need_a = 0
            for j in range(N):
                need_a += x_matrix[j][first - 1] * x_matrix[j][second - 1] / N
            return need_a


        def find_known(number):
            need_a = 0
            for j in range(N):
                need_a += average_y[j] * x_matrix[j][number - 1] / 15
            return need_a


        def solve(lst_1, lst_2):
            from numpy.linalg import solve
            solver = solve(lst_1, lst_2)
            return solver


        def check_result(b_lst, k):
            y_i = b_lst[0] + b_lst[1] * matrix[k][0] + b_lst[2] * matrix[k][1] + b_lst[3] * matrix[k][2] + \
                  b_lst[4] * matrix[k][3] + b_lst[5] * matrix[k][4] + b_lst[6] * matrix[k][5] + b_lst[7] * matrix[k][6] + \
                  b_lst[8] * matrix[k][7] + b_lst[9] * matrix[k][8] + b_lst[10] * matrix[k][9]
            return y_i


        def student_test(b_lst, number_x=10):
            b_dispersion = sqrt(dispersion_b2)
            for column in range(number_x):
                t_practice = 0
                t_theoretical = Critical_values.get_student_value(f3, q)
                for row in range(N):
                    if column == 0:
                        t_practice += average_y[row] / N
                    else:
                        t_practice += average_y[row] * array[row ][ column - 1 ]
                if (t_practice / b_dispersion) < t_theoretical:
                    b_lst[column] = 0
            return b_lst


        def fisher_test():
            dispersion_ad = 0
            f4 = N - d
            for row in range(len(average_y)):
                dispersion_ad += (m * (average_y[row] - check_result(student_lst, row))) / (N - d)
            F_practice = dispersion_ad / dispersion_b2
            F_theoretical = Critical_values.get_fisher_value(f3, f4, q)
            return F_practice < F_theoretical


        x_matrix = [[] for x in range(N)]
        for i in range(len(x_matrix)):
            if i < 8:
                x1 = x1_min if array[i ][0 ] == -1 else x1_max
                x2 = x2_min if array[i ][1 ] == -1 else x2_max
                x3 = x3_min if array[i ][2 ] == -1 else x3_max
            else:
                x_lst = x( array[i ][0 ] , array[i ][1 ] , array[i ][2 ] )
                x1, x2, x3 = x_lst
            x_matrix[i] = [x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1 * x2 * x3, x1 ** 2, x2 ** 2, x3 ** 2]

        matrix_y = generate_matrix()
        average_x = find_average(x_matrix, 0)
        average_y = find_average(matrix_y, 1)
        matrix = [(x_matrix[i] + matrix_y[i]) for i in range(N)]
        mx_i = average_x
        my = sum(average_y) / 15

        values_arr = [
            [1, mx_i[0], mx_i[1], mx_i[2], mx_i[3], mx_i[4], mx_i[5], mx_i[6], mx_i[7], mx_i[8], mx_i[9]],
            [ mx_i[0], count( 1 , 1 ), count( 1 , 2 ), count( 1 , 3 ), count( 1 , 4 ), count( 1 , 5 ), count( 1 , 6 ), count( 1 , 7 ), count( 1 , 8 ), count( 1 , 9 ), count( 1 , 10 ) ],
            [ mx_i[1], count( 2 , 1 ), count( 2 , 2 ), count( 2 , 3 ), count( 2 , 4 ), count( 2 , 5 ), count( 2 , 6 ), count( 2 , 7 ), count( 2 , 8 ), count( 2 , 9 ), count( 2 , 10 ) ],
            [ mx_i[2], count( 3 , 1 ), count( 3 , 2 ), count( 3 , 3 ), count( 3 , 4 ), count( 3 , 5 ), count( 3 , 6 ), count( 3 , 7 ), count( 3 , 8 ), count( 3 , 9 ), count( 3 , 10 ) ],
            [ mx_i[3], count( 4 , 1 ), count( 4 , 2 ), count( 4 , 3 ), count( 4 , 4 ), count( 4 , 5 ), count( 4 , 6 ), count( 4 , 7 ), count( 4 , 8 ), count( 4 , 9 ), count( 4 , 10 ) ],
            [ mx_i[4], count( 5 , 1 ), count( 5 , 2 ), count( 5 , 3 ), count( 5 , 4 ), count( 5 , 5 ), count( 5 , 6 ), count( 5 , 7 ), count( 5 , 8 ), count( 5 , 9 ), count( 5 , 10 ) ],
            [ mx_i[5], count( 6 , 1 ), count( 6 , 2 ), count( 6 , 3 ), count( 6 , 4 ), count( 6 , 5 ), count( 6 , 6 ), count( 6 , 7 ), count( 6 , 8 ), count( 6 , 9 ), count( 6 , 10 ) ],
            [ mx_i[6], count( 7 , 1 ), count( 7 , 2 ), count( 7 , 3 ), count( 7 , 4 ), count( 7 , 5 ), count( 7 , 6 ), count( 7 , 7 ), count( 7 , 8 ), count( 7 , 9 ), count( 7 , 10 ) ],
            [ mx_i[7], count( 8 , 1 ), count( 8 , 2 ), count( 8 , 3 ), count( 8 , 4 ), count( 8 , 5 ), count( 8 , 6 ), count( 8 , 7 ), count( 8 , 8 ), count( 8 , 9 ), count( 8 , 10 ) ],
            [ mx_i[8], count( 9 , 1 ), count( 9 , 2 ), count( 9 , 3 ), count( 9 , 4 ), count( 9 , 5 ), count( 9 , 6 ), count( 9 , 7 ), count( 9 , 8 ), count( 9 , 9 ), count( 9 , 10 ) ],
            [ mx_i[9], count( 10 , 1 ), count( 10 , 2 ), count( 10 , 3 ), count( 10 , 4 ), count( 10 , 5 ), count( 10 , 6 ), count( 10 , 7 ), count( 10 , 8 ), count( 10 , 9 ), count( 10 , 10 ) ]
        ]
        outputArray = [ my, find_known( 1 ), find_known( 2 ), find_known( 3 ), find_known( 4 ), find_known( 5 ), find_known( 6 ), find_known( 7 ),
                        find_known(8), find_known(9), find_known(10) ]

        beta = solve( values_arr , outputArray )
        print("\tRegression equation =>")
        print("{:.3f} + {:.3f} * X1 + {:.3f} * X2 + {:.3f} * X3 + {:.3f} * Х1X2 + {:.3f} * Х1X3 + {:.3f} * Х2X3"
              "+ {:.3f} * Х1Х2X3 + {:.3f} * X11^2 + {:.3f} * X22^2 + {:.3f} * X33^2 = ŷ\n\t check"
              .format(beta[0], beta[1], beta[2], beta[3], beta[4], beta[5], beta[6], beta[7], beta[8], beta[9], beta[10]))
        for i in range(N):
            print("ŷ{} = {:.3f} ≈ {:.3f}".format((i + 1), check_result(beta, i), average_y[i]))

        y_dispersion = [0.0 for x in range(N)]
        homogeneity = False
        while not homogeneity:
            y_dispersion = [0.0 for x in range(N)]
            for i in range(N):
                dispersion_i = 0
                for j in range(m):
                    dispersion_i += (matrix_y[i][j] - average_y[i]) ** 2
                y_dispersion.append(dispersion_i / (m - 1))

            f1 = m - 1
            f2 = N
            f3 = f1 * f2
            q = 1 - p

            Gp = max(y_dispersion) / sum(y_dispersion)

            print("\n")
            print("\tKohrens critetion")
            Gt = Critical_values.get_cohren_value(f2, f1, q)
            if Gt > Gp or m >= 25: #because 25 is max number of reiterations
                print("\t\tDispersion is homogeneous {:.2f}!".format(q))
                homogeneity = True
            else:
                print("\t\tDispersion is not homogeneous {:.2f}!".format(q))
                m += 1 #new Y column will be added
        dispersion_b2 = sum(y_dispersion) / (N * N * m)
        student_lst = list(student_test(beta))
        print("\tRegression equation after Students criterion")
        print("{:.3f} + {:.3f} * X1 + {:.3f} * X2 + {:.3f} * X3 + {:.3f} * Х1X2 + {:.3f} * Х1X3 + {:.3f} * Х2X3"
              "+ {:.3f} * Х1Х2X3 + {:.3f} * X11^2 + {:.3f} * X22^2 + {:.3f} * X33^2 = ŷ\n\tcheck"
              .format(student_lst[0], student_lst[1], student_lst[2], student_lst[3], student_lst[4], student_lst[5],
                      student_lst[6], student_lst[7], student_lst[8], student_lst[9], student_lst[10]))
        for i in range(N):
            print("ŷ{} = {:.3f} ≈ {:.3f}".format((i + 1), check_result(student_lst, i), average_y[i]))

        print("\n")
        print("\tFishers criterion =>")

        d = 11 - student_lst.count(0)
        if fisher_test():
            correct = True
            print("\t\tRegression equation is adequate")#end code
        else:
            print("\t\tRegression equation is not adequate")#cycle starts with new Y array until got adequate regresssion
    except ValueError:
        pass