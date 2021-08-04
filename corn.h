#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <stdbool.h>

#define foreach(b,a) for(int a=0;a<(sizeof(b)/sizeof(b[0]));a++)

void println(char *value);
void print(char *value);
char *fmt(char *self, ...);
void print(char *value){
    printf("%s", value);
}
void println(char *value){
    printf("%s\n", value);
}
char *fmt(char *self, ...)
{
    va_list args;
    va_start(args, self);

    char *result = (char*)malloc(1);

    while (*self != '\0')
    {
        if (*self == '$')
        {
            switch (*(++self))
            {
            case 's':
            {
                char *arg = va_arg(args, char *);
                result = (char*)realloc(result, (strlen(arg) + strlen(result) + 1) * sizeof(char));
                strcat(result, arg);
                break;
            }
            case 'n':
            {
                int arg = va_arg(args, int);
                char str[(int)(arg == 0 ? 1 : floor(log10(abs(arg))) + 2)];
                result = (char*)realloc(result, ((int)(arg == 0 ? 1 : floor(log10(abs(arg))) + 2) + strlen(result))  * sizeof(char));
                sprintf(str, "%d", arg);
                strcat(result, str);
                break;
            }
            case '$':{
                result = (char*)realloc(result, (strlen(result) + 2) * sizeof(char));
                strcat(result, "$");
                break;
            }
            case 'f':{
                float arg = va_arg(args, float);
                char str[25] = "";
                result = (char*)realloc(result, 25 + strlen(result)  * sizeof(char));
                sprintf(str, "%f", arg);
                strcat(result, str);
                break;
            }
            case 'c':{
                char arg = va_arg(args, char);
                result = realloc(result, (strlen(result) + 2) * sizeof(char));
                strncat(result, &arg, 1);
                break;
            }
            }
        }else{
            result = (char*)realloc(result, (strlen(result) + 2) * sizeof(char));
            strncat(result, self, 1);
        }
        ++self;
    }
    va_end(args);
    return result;
}