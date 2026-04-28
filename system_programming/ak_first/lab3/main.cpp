#include <iostream>
#include <cstdio>
#include <unistd.h>
#include "getopt.h"
#include <string>
#include <typeinfo>

using namespace std;
int main(int argc, char *argv[]) {
    int rez = 0;
    int option_index;
    const char* short_opt = "h::p::ecl";

    const struct option long_opt[] = {
            {"help",optional_argument,nullptr,'h'},
            {"print",optional_argument,nullptr,'p'},
            {"easter",no_argument,nullptr,'e'},
            {"creator",no_argument,nullptr,'c'},
            {"lab",no_argument,nullptr,'l'},
            {nullptr,0,nullptr,0}
    };
    string av_opt[] = {"--help | -h", "--print=<str> | -p<str>", "--creator | -c", "--lab | -l"};

    char used_args[sizeof(long_opt)-1];
    int use_count = 0;
    bool use_flag;
    int i;

    for (i = 0; i < sizeof(used_args); i++)
        used_args[i] = 0;  // заполняем массив нулями

    while ((rez = getopt_long(argc, argv, short_opt, long_opt, &option_index)) != -1){
        use_flag = false;  // флаг использования аргумента в прошлом
        for (i = 0; i < sizeof(used_args); i++){
            if ((char)rez == used_args[i])  // если аргумент встречается
                use_flag = true ;
        }

        if (!use_flag) {  // если аргумент не был обработан ранее
            used_args[use_count] = (char) rez;
            use_count++;

            cout << ">Arg: " << (char) rez << endl;
            if (optarg)  // если есть принимаемое значение
                cout << "\t>Sub argument: " << optarg << endl;

            switch (rez) {
                case 'h': {  // если передаём аргумент для -h, определить что и вывести результат
                    if (optarg != nullptr) {
                        if (strcmp(optarg, "h") == 0 || strcmp(optarg, "help") == 0)
                            printf("Show available args of info about arg\n");
                        else if (strcmp(optarg, "p") == 0 || strcmp(optarg, "print") == 0)
                            printf("Print specified arg\n");
                        else if (strcmp(optarg, "c") == 0 || strcmp(optarg, "creator") == 0)
                            printf("Print the creator of the work\n");
                        else if (strcmp(optarg, "l") == 0 || strcmp(optarg, "lab") == 0)
                            printf("Print number and type of lab\n");
                        else if (strcmp(optarg, "e") == 0 || strcmp(optarg, "easter") == 0)
                            printf("Use me)\n");
                        else
                            printf(">> Unknown argument '%s'\n", optarg);
                    } else {
                        printf("Available options: \n");
                        for (const string &obj : av_opt) {
                            cout << "\t" << obj << "\n";
                        }
                    }
                    break;
                }
                case 'p': {
                    if (optarg != nullptr)
                        printf(">%s\n", optarg);
                    else
                        printf("Specify an argument value to print it.\n");
                    break;
                }

                case 'c': {
                    printf("> The lab was done by student of group IO-82 Feshchenko Kyryl");
                    break;
                }
                case 'l': {
                    printf("AK-2, lab3");
                    break;
                }
                case 'e': {
                    printf("Hey, it`s Easter egg!");
                    break;
                }
                case '?':
                default: {
                    printf("found unknown option\n");
                    break;
                }
            }
        }
    }
    return 0;
}
