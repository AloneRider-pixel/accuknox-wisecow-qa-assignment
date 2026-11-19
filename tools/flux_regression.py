#!/usr/bin/env python3
"""Ephemeral hosted-CI rehearsal. Never select or accept a user kubecontext."""
import copy
import base64
import hashlib
import zlib
import json
import os
from pathlib import Path
import subprocess
import time

# Exact reviewed restricted install fixtures, compressed only to keep this one-file CI test portable.
CONTROLLERS_BYTES = zlib.decompress(base64.b64decode(
    'eNrtfWt72za27vf8Cm7tPttxx5KdS9M2M5lu101SnyaxH9vtPGdXOTVFQjIbitQmKdvqtP/9rAsAghQlgrLkS8t+aCyJAIEFYGFd'
    '3/XvR47TcSfBTyJJgzjqvHQ6l086O/jtpyDy8fO7IM34myAT4xS++hk+OM6/6f+LmtMvqosP7likE9cT+U9jkbm+m7nws+oIvg3d'
    'gQjTwnf0gknv03QgkkhkIu0F8W4QpZkbQX/Quet5009RfN31RRhcimSmX7Kg8cRNsm48xLbDcHpd9/ilMbenvSd7vb1ii0nsd1Ph'
    'TZMgm5WaXrkJtUtEmiWBlwm/UdOu8erQhR+yjm79R95RJwLyVlNCPvPHI6PJgnWDN1/FCazYqPfpK5541UryU8dxGHizP8lqLqdp'
    'GMZXXTGCJUw7pd95Sy8lvKZQOhFekTqyT3Wc+L9//6E/fDTeBqtS9bDxNzw0TOJx6Yn5p9S+OxWh8LI4wTH9UXqi+Pnjo6pfzNGV'
    'uyv8hBvlbDYR5cF3DqMyUeHL1/zdo/LLbXYwfBLXmYjwc7psEx9M0ywen4g0niae+E4MgyjIsJOa/exGUZy5+OTcpvbiKEviMBRJ'
    'dyQi2nODaRD6Iilvur3e0ydlFvKJBhT8JnpZHIefgqyHW9nzsW06HaRZkE0z2ml+kLqDEPhI5aa1PXBePJ7EkYgy7JKp0M1nUHeE'
    '7vNxHUy9TyJLezypeXLaHMxREk8nOWUqOinzgbndAMx6FCfB3KZ3iKEUJu0wITy/+tsuD8I4EoWzZ+zqb2nqRYKGcHf/UPhd3+b5'
    'EQ2niRsaxCv+nALvmYZukj9QvQKpF09E4bI3Z9SRC1nDwlzfp5PohsdJEGUiOYjD6ThK7djar2kcHbvZBY6ih+vaE5E/iaGjEm0L'
    'W+b1kmeyGc8Jr+9o1CnzyZ2GY1JspeclgvjIWQC0ytzxZNkA90di2digQ3HjkcEgsmnaAybAC5D+/M3j/+7hK1696ndOhOvP+p3t'
    'j/K5ZaOlZ2+BlrYjBgKnbjUF1ZBPF06qZszFe7J0flXvxg2kj8qFGLslpkG/wBGK9o8Pf3p2uugReMgXqZcEk0zyRT7XTpA62YVw'
    'uKEzjBP6KI+0A532qiY4SeCVSRbM8TCDJxt3bNUT8yPCGXATx8fLVfDQJAsQvsMEcOIhfA/jTsQEbn24juhM4Ncu/H/wK0gUvX50'
    'KhJs6aQX8TT0HVhw+JhBIy8eRXBnqu7gJTG9h0Vlh/gHcBLn0g2nYgf69PvR2J1BS+zZmUZGF/RMCm97HycCmg7jl85Flk3Sl7u7'
    'I+D9UpqAi3M8BWFhtkvXZTCYgsyT7vriUoS7aTDquol3AWqSl00TsQuk69JwI9qgvbH/n4lQ/HynmpTLd1zlSTFvAbsFwisBN4zr'
    '8Gt4+vk64FdIyZPXp2eOGjKvFS9L/mhqrBASF0gnEn4U5VHqRnFh+uCFATRzQKwZBxmu/f8C4TNcPOjpgEQsZyCc6QT5mg/fHUbO'
    'ARyl8MBNxeYXCOmfdpGaa1+iSqGysmcmsn3PczJMPb84hSYOtguGgTyfuBRBIuiIDYMRSAV0HOFUAZfwp7AD4FjuA7MYurADgMP0'
    'I31OYSPFCbBZyXB6i2hXy2/oKe7kAzPQRU8tmhk2U9wQeTCzGdFsoJYLvXBJWAyEmZ4KuOuzEzFsNJMDs6XjAZnhSIxAwI4K03Id'
    'fghXLHNBi4lG/UgE8EjiwAUwiLMLeKwf9aMuPHv8+n1XRF7s4xLzKcQRwgZAedV5fJ6FcJ8m2fk28kpY9OASvu9Hn8RM/gh/nW//'
    'fb63g/1ST57LHeGrsa+riwB4NDAJx4XTm04nE3i/v+NcBWFIpz2FXvDOgolEsErEgIib9yO5UM5ZzjzwZTRGHBr2CO2H09AJhs4s'
    'nuI38NoptIZzDSPC3q6AKjBqY5h/J1LKoeOG0Z30I9kLfIVtgU2KcNgF9kGXF3E7sycem1yKMehyMGjedrCBnPOjiQs87hxX5Lyo'
    '3QBNz3tIozPil4EIiS3HUTgjIsVJJumCQz0HzVIkgXeO5/EyQN1y2e61OmqmpLLsmfkt+sE4WokApg/EXjaeBidqXrayOm8OGtqY'
    'hVXoC/MzXvjARwuesJhFL+cJWiNpwg6UiqLYWomVgdaEVhP6qcgDwxj3p++4m2V0cDDgVm40pUNq4sRwlBLYyjz4FM4PbClx7YVT'
    '5CsTN0MZLoX7nn6Xaj2/Ds/F2IWz9pi4i6JNilMHYbAHUgE/uN1zDocOyhXy3ADjcVEydadhVmBBO31gaFGKX2NXfuxNx1osxWMI'
    'fCFRciwyqCEKUvEUerlwsU2cCuQbmyV2RCbjhuSWjRyyZ6YlPusCdaLu2btT5/uzs2NHbTeraQziOBRutMo8YG0vyfLQZB7cCHY0'
    'XyrGpnfMYwLXDXzHzJNlSZRUic+qF5MEPIE9cR2M8drCCwVF2AHeUHzCgDa/BrgH8S8BOwNvFjEEtk/3EOwZ3K9aqF/Oj3kz4yz+'
    '3+Of97pff/zb436/x39tf/N4nP6e/j7+/WJ7+2+fbXL/gOA+DK4bUf2YmiANcMZIUr4E4Ur04XMQwsRwKwEt4IPQ5/XbzctY6iqs'
    'mw8ddnyRvESXjWlu9vyK5YJkP/qOX0J66JZ8zdaO3KbiGmRt+A1EudNnzmNQkbcdNMMCbxmEqs9+JDtdSjIRTcd1F1z9LFG1v0qX'
    'PzDyJjU9/IaM6EYX6Q0W/nq2mnR9XGha0oLmJGr6lt5WVIz6kTwPsMCwglLzNMVNgzXxeWnltQcnryVitMz0VUXpE2qiaK0vpSvQ'
    'ysQSGS2INsoo05WOiv0pMfUtmD387ONHN0z7kdJgLO6D9hTcx1OA7CvwxL7nxdOouWHmdK55lYHmB60bO8UGbB5AOTXfYyCH5fZt'
    'VMAtFOgtuM+2SMzbgqtvS6vRKBm+gWfGyrSIegVuYneAsr287wPaz9nsZT9ShsfcS4t/7aJgOeLLId3lVl3VanejZztLm63H2am1'
    '7Q9vOLIzUZSKcxZ/EhGbfGGBiLRDkXkXdFGKMVDcTWbm6S+vG8qGbj+S96K2ZNhbQWDpzmkR5+0h6ZpYi73hrjXeLTfe4U5TJo/W'
    'hOech747sbPfNduy9jfium7Fhjfj8tux5oZsckta3JQ1t2WDG7N23Hb2PhubH1pmdvPDpJaryJgdzZeTeNyPpMhZyZbV6SXuLfz6'
    'rWiaL/AC/J1uwW24Bnuff7ZGEWopOa3UfRslvpputVSw0L2tVGuOzgFmsJ5delOypitfdutVEMrXRZCaPFn1Ro8Sq02dc2D5CR73'
    'c76sziduml7Fic8yAnSQc2Fiyi0r/hOz4o2qX0uCyao41N0oalM4hksiQSqPMLeBeyIM+fDmsaAoyKXqd9qS8JsXhIEO1cFQDyXO'
    'b9ZhkAVjAfqYtaX3xV7awMp7xr3nGo2D552VuR3lLSJtBvpdg6F/TWb+Rw1oaLPTzdiLeidmvXPnUYMTUN79C5667uYieBfeEfg6'
    'JnvRrJZsGBUfKNXiov67xJZAFgSyJShTv1PSaZfuvmQa8vKCWtJTLZxXr2THv//uzP+iXwS//seFmz6mR0D53258mOwIwmNRTuci'
    'IZBYenRFqpTo0JwM/2GQoThRTRj4ME+2TZEBRYVmdFi0J1ajxeKFX0wPGvOGCEKx1fhGLTcicdDDru1IxR1hEsmGBDaTXLhJ8lFt'
    'b3r+BUPRvaJBYWSbokO1XRdpUGV8vY0jMTegTU3d40hVjFghSx3nG+TnAW8G9d2c7bzZ6utVXH2u1bewfXwpB8gviTBVQtfCkM54'
    'QEY3/y2umyuFru6TRuJLdSArjY0E08RX4VH8LgfHLW2t364jLtWVwa+NxGsdMZvHTMsw9RTPiefBpkKjpTwWRQl7TQZtPxhh9mhT'
    '5f47aqYuPu5EKacY6KHiPNBjgt9v/cMNMe8puxj/8+U/KAQnnY7/udXIuPSz2/2NheZvXv7c+9sv3Y/6m+3PX+Lf+93/gY+v4Je/'
    '3ZrhCVfrR4ojQkWhMSXfFZorimYq/QfEzgT2xgSTWbT1nHcIBy9JqvcjtZtqScpeLJUg1MVX3RatagPd8wNl5Hs1Ma80MXbUGTNK'
    'K/VeDt65iNG+NJ3AO4Q7LvgF4dReYIzh0cGhYySFWjuSb2pUnnASVEMLKDRSGy8RIQz5Up5i7E4da72/nMNM+a6U+5UjFdjxah7/'
    'JI6zcnsdHhXzM9g25FbpLM3EmHxbJWPD2I3ckQq5OeXsy9vatIm4DNK6UI/qcA9uyAk1F1OYRBd2jI95utJpPAzQkpK4nuAvmSTA'
    'KGGyDscO9iMmi0l313kbZBRYBP+cfr+/Q58zd4Txq9+LcOx4F3AlqYDUHUdk3q3RKw1+a84GT6GRdv1PxwO2xw9mWR4ziFukAXML'
    'ouzFc9s5k4N+mWmubtLTJGw85x9P3pk+HB2tXT4wwE/E9STGszaYlcxwmLg2fzQqjihIikkgLkWxa8rVocjmMQ0Ldkpv1MPXuMC8'
    '0OFsHEJ3Mgln6k26C3yA0r0eSrCMFHmaXOr1PNeOg9RuoTsxDeeZss1SkXQzeSPKnam+bBDbpfBjlouqC16vnD+p48MNHYT85jjC'
    'YH8MrVXnyZsmCSUYZlpsCij/1VGAD71aA76tJEIb6CxxozRQ2dw20ktpivOdKH5BAiBKbkWi41Uin0YFG9MskQ6spVG8DZ9qFfAu'
    'M2cHGKoqg1CmESjSfMzzbuE2iUbC7zmYL5FhRoPU5j9F8RUwDfTfyXgKJb3mPSKFOfxBdkP3IWg3kwwvvXof1goS65olwVy9b7qE'
    'sqUhAjhaBNC/AZllJIvawRxfRrTUK6oWTWYiQE8CmPZMZupakHHsXr8T0YgkxGdPv3zx1a3SsFLPb0rO+U7KynMOpTDKn8k4Ccc8'
    'KVdwq5KNxsULcjoh+mKsnwIx2cGIo8reMImEeUk4c5483XEGcq0qoAeuP/Yqxgw9fL1TGhB6FKbErHySpSmoCVU/mW6ygIUJPeBG'
    'B8lGOsItE0TBmAIb9qw3i4UsZeNIdtOVdgg3zO8EF82Jo8Qdo4bmmWK3cexY86GG6tbSC7OVSm5rHsRjzntOSFiT8Q2eyYcxWZxO'
    'KuMcyCwPjSfAKUXCxfgHdVOqKLEdFVwnSAAjgATZKKFxYW4NWpFdZzR1YVSZgA+I44AMQj5ssHY3z5JXvKIQlIajlLn1xFAacpIn'
    'e0+f2+yjvEHt0wWjz373f9zubx8fyz/2ul//svPy4+fGx4/b33x2u/dBjdlz8e6UN7GSSNR+2aFrGr49SxCQ4o0bpvDPjxFdrxbr'
    'YRl8BE/iC2yCRmgINg/KQdaFlXy81fWRfTVdHQrphFUwmLIBMeHQ5QCHNe6Ja3c8AdEFNPDdHIKi4Q385EWjg/BYGTsf/9yVf32u'
    'vtr+huIIlj2w/fkuPGWcoo8/d/Mj1Pv4+fY3xm/b6z5QN7C+WEYUVYnclmKd3V1kxxNsduajFc+JtZnwDwtt0U0Sd9ZcWUQqfw/3'
    'Uyj8E+mQEPvN/B7vKrswlEi+wSSTHMcp+T7g3u5HygciFDyMwvBJMVeZ9QvVMLe/8kP9SJpEQMimu3ijWVUNxd0yjY4qhUat+mlH'
    'liGWymlLb5FESVo2RXtp0Fa2qyfHYXNAgKNC0xzpQFKAMAHIzKpBAcy8A1i/KWUesE1ZIha5Fs6SG2+BOpvgEnugP4vcMUiUHG8W'
    'BtEnLZhKECttju9Hh6SOKwgDtKu7Tr8zwKfEEJpl/Q6qOUFKUFeGng6KkxekQgXpscO0py175OwI2IM6HovIX8+RaeTZtQA+emTR'
    'V00/xT7+KKOy0UaD1hlKZ6Xf2Jmx4MfpIIf1qgB1y8XI0gCqgVVbxNMW8bQB4iluAIS5U7zuL4l9+loSQTG1xSio5SeX4aHOkbaE'
    'jHoBTPeDpEFppsJdPGgTUbX8ioeBrdrimP65cEx3VsHW5cN5Ioa9qDqmLR8XPflQ8VXLHGMB0qo6yVroJKdTi7naYq62mKt/eczV'
    'Mg8h9FXznMLzFDKuXT5LJZrGgauaVzdLDFOtHNpK+rAbQB0eyfH5fqVIkxyYzTV4prRh1GiX9jGtFkxyCbPUKH6lXEvyB1Jkt0xn'
    '9ctTntCjuFiqCxMI4dbir5Yyn6VMaIPwNzsPDrCndsSqyEvzYVPL+f1FERPFHRZkDgkMcJ++wzjJI+JFJ9xkvTGQG425oj25c6cQ'
    'Rus2O62YD7Gc+7N70OT/8ykL670A1pq5EE+zCccwgMw4Jx63CQxtAkObwHCLbvA2gaFNYGgTGBrTq01gaO6wbBMYbk+YbhMYSu03'
    'nMBQFmTbVIY2laFNZWhTGdpUhjaVwWlTGdpUBlvzT5vK0KYyNF2fNpWhTWVoUxmW97FiKgPaJBCJ7DCaTOvqJKxgzi3CUZJkB7JT'
    'd8pcpsswxTJweKXpzzmTzOlIldaFO3FCNzvFwU/xsiUbcDzh6YDcJ67RgJcpNcsIk1feew4yl9I61cOji17yjh00t/gwJ2lPZnMM'
    'RQlJazICjYcsnwDPIN9WGHwCyVCpq6eCBEPZEoeQojRIE8E3BfiesQqGyXsL41HgWQWl37J3sA1Kd9qg9PLCtUHpnVEAPGISw8VG'
    'keB/xZD0t0F2okgwWxyPXnhsWTB6iaT2oeiyoV08uvmW2cMIRqdgZDRKL4lA/vHk3S2ERbdh8X+usPh7EX5eYBALYs9LvIFMK23k'
    'eRt53kae/+Ujzwvsg8LObQv/TdhiDCcpD9oijsNRHbmYcENQ5bZ4/K0WjyfqNKy5Tm2MjeM6KMIitYu3k+Z3sui12jZpP8qt+3II'
    'vloXvbfkhvNz70Kh97X74wu9V06SQr4SFYZN7ujSjGmexvl4DJyuu61iTbhqlTFnTs3XlYBnhtNjEqIkvUaHPjLkY5s4u3nKvJFN'
    'S7yCwuzIfjOZ6XgaYvzFAjkqpK4flWPybtfpYWgyzWlQWOf5+mYV22A+1ggkkNIGsKBAo0JjTUqNra/YWONyY3UFx2rXslnRMauy'
    'Y01cPPXxrhYunnjF03gWW5/FLJ4/ibLeLMeqlnd17+F5TarsEw/QLaErZDW7irmR42ZOnmVX5EUyXJOSF+RlyuJ1qrzo6tWkFEyA'
    '31wHYwzPIBc/W//hGvtVhnH8GqAchX8JkG6wLq8YDgOP5HosDg38Q9/7a6iL9vvFmiqjLaS8VQ3RhfVDNepQsZ7ljgpkpXo8O/DP'
    'b0Ar/ANEyYvpgP6SNWtgHf41lwRWPLj5s8soYeFF78iOlssVdeVKOzSb5Y/wPG8WGnqDJb2e2VXsrlhYo2ltFVMGVIImRYUJuCuX'
    'SodTGQpHKqZm4Wp5UGXt6TWlRd3LlMqNRkVvPIFw4R5LsGJwKk6ngzHoKaFoFoV8Um4N3BRdSKmMiAuwEm7wW24TA8UyzR/GLRRE'
    'FXc4aqtemEfP4gNwA+zkwa1BotVVUJFxQ6abrdOZNDyBOs91XsQuKl94zYSX8p6KI5y/zAygMN10XvbZGrsp3DlbziBx4ak1nTru'
    'rPG5+5aakdCGdzOq/iWmr0ZLKegOJzbokvJsXL29BHNO22k8ywOd7VOaaeZ+4ux5Dws/e2y+oX2eLzJHS8D9KCUVeafCUAY4d+ak'
    'OR3TC2geX/EBoAXnpdlB24JUzTlsjcYUpHlUI4oz10H68LLf+Shouv59AV2/lYQ4c0d0Xk7F+CcKo+cYD6mWug7VTy0etYKptZt6'
    'Y4oa82MvpS/o1V14uss2tP/8xRh0P3rN0SLpS6ePnCDdvRCun+6O4f7sd3bUl5k7Sncv93pPenvGt5NpGO4+f7pHbYzvxyIZia4y'
    'Hu8+kb/fWqaYGF+uUHKeSY7pbrjtMGVKGv5qDwUs2q3tSxhe45nhprKZx7e1XPdWZIsbF9VeSbC0lymLmoQDP1PMt8uJQRWXvgz8'
    'x2y8U6fg+TNeQGdcvsXZAtk0QRYkaxZP3DS9ihN/qx8xzyWVBuFDPRoOho5uDYSbiOQs/iSiLXkPkWkWv6Cn5DhOT7+3HAUHs2ez'
    'LY4Y36IYuV8uYjjVW4r5t5LxQ5OMKyqcNjsoVVVkDdNVGYGn2ECljsKWys+RUBJg8dw4RhZBdW1vqbfzKaHSurqc90YdM+nEBfXg'
    'ADmqRY37Iv0KTSvdND5sIE8dTsm42fMEJxmlJ42cbLj10PFlmCeIWByyaXbnJnMuHcMfsnGfju3p26AlL50ClWrAmObWjNs4mQjD'
    'tJQrTZKt+p2WxARUUXEU/ciekjdW6TCB0WJbqirAnRd7y+xJc+IE9057BCVR5PEc30nxw2qDFpUleMUarI2btjWuAg5epQWb1t0d'
    'xItSCAsRSQG7p468h2Vyvj1pUNb/nQT+39P0Yhuk/t7nGyUJCIbBcNaIKj9hEyUeFckzF7bA3WvSserXj9JgFLkYBvI43V6TiDGO'
    'fSsRQ5+K71/vf9dpCOYSF3zSbPOnM0J3NUzGcCHT1AMKo1GJdUngol+o32GNia61Pg0E0eKxcDnG3M/y4Ac0M8FJC3qiJ0lZUKF1'
    'Xip2oa7m0hbVYIF43epBwJjUIFLgQpSQEHAokHQsgPjpfbpysYo3RkbDig6A6dWn99kmk9Hr6/1dFqvkkApk9dB+5FOHj27giFyj'
    'ImujyNxMmSED+XQQgiLxScw4czABJUCQlYGFtBiEKef47XHhQWWTwLQGTHDGtH7+RdvPe27qwdU4HAbXMucUWV7TToDNQRPZTz2y'
    'VyNcJ2tn/Lpc8Q0d8X/cMKDC2gVv4YD/uD6wqY0qVvmpuTfAhRZDzx3MS4WTRw2mU57KgqcKCXFkX9TJOosGu0QUyJEsKvRMEoNI'
    'MRlwACApNEpjQxVP6XOk2oE6t+zqT6Yhvec/Ltz0cSrCYW/+jdvO7787j/UD6lXbzn/9l1P8ynn1Sr8d2lT8BsPZ3m62IT6uEaNS'
    'ySX/blTcqPuk0U5dGo7KueWo3yT+IhzMNUebrhUIk2AW0qnnwR4dTsO5aMgWCLMFwmyBMNcXXdYCYbZAmPU0bYEwG2qFLRCmvXGu'
    'BcK8df2rBcKci8zZKBDmZrNuWhTMFgXztgTCFgWzRcFsUTAtN0uLgtmiYFbsoxYFs0XBvK31aVEwWxTMFgVzeR8rp5tyiJ6GZFgF'
    'AiJvbV7UKsiwwiMSznRsYG7wpjp3KP0gVCXbSOZQSnryjWtXPy1qmkmjTAP/TUMl09KHc3denE36cdZ8ZTT05twDf879UIwt/Tqr'
    'e3aah6bsNFy5Dfp31gz9MFkN+OHP6edZO8iLpbfnoft71q0L2Xh9Nub3WcWosVZDhY3/56/uAbqHyoKFL6iZN8jGH2TrEarzCT0A'
    'NQEp970b+aHwT6T4K/abBUu9q+zCcDmxoUsemXGcErqnwAhxJXELBRSp0DxTRF5jN4RqmN/m/BAcCj4+vsjIZLfRdK2GVvEyjY4q'
    'bctastRRcIb1Oo+1zzWlfiRxU5dN1Z7P2nLYerIcNsd0PCo0VeTQlCBYR7qsNa6jRuJBbkjKpM5ikximrk0pv3VthcMVoBWPim3n'
    'Zl0Hs6hTHxVYp+lt2FghwxY4cRFlWuDEFjhxrUpxC5zYAie2wImV9+3JjfC4jhb1MncHa0T0HI6LFDAj7VRpbCvfwjdO0FajPV0d'
    'RuCosouFIomJAXBLYsh9yPWnrWDmI7+BoYhkglVMmiEALOtJUX1ofCWvGzPbEelOyING0rNOdDazc/NsYR0nUV4dwoUK9FpKNUoq'
    'XZonXpqZ2JMYRjLb0UZWF0cFWpzUy3Y4fkcyqMJblTqN3RqJy447coNoszgbc2R/HzcU2k8ruygocETEAq3G9IgOXelHVancF+6l'
    'AHqIKE/lXgMt2qJn8/EfbdEz1boterbo8aZFzy5EOCaz/l+y3hl6NQ5w9otrnelHltU5y6loX+LswrOrbqb7fkCVzbw5mpa23cGi'
    'B9ZdkQtHo87EkvH8tPiRTYyINyhqZLQTl9UBYzH+hwWPbXZwNIj6wX1Y8Fhbqa6tVHffK9Vp9r6gSl3O2dsCdW2BurZAXVugrsA1'
    'KorTwaNUm84AA8mDZ24IBMJyVaP8SZO3sXE4keZkjAfJo3pwK1+6QUghQ5h0J1ExT7U0sNESb+RAfR+kKPn+RIzkTdDUPHq4oBMV'
    'XJLmeS6xk8IvlFQla+uNuZnkYogwjC0TV+bFADcdAnVqkt9ubhNdY4Wd/GrTa9jW2KkplsGRHKdZgtrozBo6lMi8WIdYHMtXeiEZ'
    'MJMxXfdUYNGst6HEXuYpkbjKQwX60U8EiW/kbj3eMgeFlXxU5ODWNt03oqLio7S+ym6oYFCEQWGhG8kHIlmdYyAu3Msgxuze7wwX'
    'lPlOzsqNx7hN/BuXBLIksZNHSN5NVR+tPa1gnpUndK5wQh5yxxuhimGvCarJQlS1EFk3CEe+dOmXSnBLJbnSiHdkjYnCgUKGmvtT'
    '8UgVHKxbO/1o69spMNdsa3tt+J/Fl9Y7cAtDqn+cx3s/kD7/evD3C6w/1pENGwXIvyOE8Hp4jJtLWZcrSpimUIn8N3LckDRkynJQ'
    'XmZ1fdJjssSam+asux/JJx5LlXnmjkOFcqFh6QczFdyxvVMoAYSh+hh2KnMrSJiXUey5sE4SQT4KZGBUkMbP0wF8DoMnPZOGrtFm'
    'yR2IDfuRLFettNlhkKSYtEEys29/wz8UV/mqON+zPLeQy3oTwjDpWyWYYYUrbLjE+5HyX1e6xFH6LqNpa0xOub1UfQR00bKKg8lD'
    'IL1LOBBVZKKYjT9fTeIqB1cpXjwqOpX2CJmJKYF5K/YCLA3JeoYv8HSD1BJgXTMeKe48skdMKbpabb/peAA7OHSlMKMk2R39vJUz'
    'uQHuuZt5F0eH3x0cymoujS+a9+UeSnq/KhPj0KsI0yaBbZ8Erlwkcp+HMnCAEhyAf1COl4okZIoRWgisPkKF0EocxPgRtwoc5ZRh'
    '4VERJaRy1XgrzUdAhdfEWLMLHaoQoFlwprP/dKEMHjPbnzJcNAxpSLPCvGovVZszXhnDY9CUiGwQNp7kME853YiT4roPuWyKGiII'
    'YIQBT8NO0ykmk8jbRumtCg0hb72BIE1+94phmoc88OLmSsRIXKsoclzV0jrFBdx7pKgigDxvb6ahF8SFedP2UV3q4mp0OWF1Nczl'
    'ISekUQhsU+GiFtgPcgFXJOqpXP6bUFUfL7WXGpC2H5mF626TtLcciSu3foMFvV9huzbiQ70mY1WtuWxE8ojNN6y1oUs8F3d2JryL'
    'KA7j0UzHxtEdQtwBrhxrHF9bNdVq8KjPyICgP2ttiULFr4oyE8BK5gXAtp5DgyP616znoDnKndgCLi1MgiYr+7yBEVzZDANDQ1Z+'
    'boermBrX5I7018gkOvbMo5e0VFqMBD82bjnKB+GYlmrp4bbWYDcRt2pTEWNRKFXZX2RhkH5QZTNk4BaqwwvU1IpIKiqeUTLTNiue'
    'wa/c1sUvSv1jCYxy/3+pWhi559umDkbBDXmfimDkyElVJTHaIhhtEYy2CMYaZb62CEZbBMOCpm0RjIbqa1sEw27ObRGMO1Fa2yIY'
    'c1ayjRbBqBW17X2xbQGMtgBGWwCjLYDRFsBoC2As3iFtAYy2AMbGeVlbAEM/2BbAaAtgtAUw/joFMFpkWzs6KamPlN8PdeEPi0DE'
    'dOtqXFs29FFML4qzOnaSLUVIrjQO8wd1Bs+fE9NX2xruLZ4vW+iU9ezExra8EF6usqtqUmnrvXpMA6MWsoZ7t5NYq4a1ak7t0Xx7'
    'kowL/l5mIZxpUO1SzZmJ9KkSchtHHZtxH9IAPV+RR/Mi3w4g+aEkHNRZs5dYsv0Z8CJQhIYCg1bDIPqk9SkZ3DKHkyejiHz0CLlO'
    'vzPAp8QQmmX9DmrnQcqgxbl5CfR9L8Dg9ZLnv6fN0uSpCzgUYDzGBIAWAa5FgJOvaxHgHgICnEbZDcRfFgduQdbsHBhc/lwdIpxJ'
    '1Qa4cLKlPTpcFUbyvYeIw4tvCaoU3HMtpFgLKdZwzPcGUswIRF6MK2byhxZdrEUXa9HFWnSxeQZSATGmzLROEdHfAPN3I6NMDeH4'
    'cLBaYvAlUNSunf+7//7dTQOzSU3HKjLNQrN1M7MMT+Tw984BC9cOClk8gzCMrzitOk7TbqRkGTQtSEubZDD6EMBm/HB09vql8wGB'
    'FdCJgFBHWJiHFOGUxBk05gFDM7bqxXRAzgaWIumfp7uTaRjuPt37+ul6osH18E9FSCUJ0pWQT4pdaIOUBKLQL8FcBvkIUEhBhGFA'
    'zsE7CjYLiLUeotGEbTAKEwJtPQKZD551aRbAWkmjAGNJj04cnLBFreEb5IfPzVPOJse0o1+XT21fBXCM3QmShhLN35Hyp81QsMPM'
    '7gK0kWABL7ilNpAkPs5HYJvUvHJV28YuJCvPX/VymZSlG0xS/N+fxGyHrrE/nIkbJGnP2XdwP4Wi8Js0ARrkQaFggn0h24On8Hai'
    '8CpH8InG7un51zpPjPAn4lRgfmWOdtHvYLGHzg4b7HnroqMRfzmM8AeFF6CDABLXwPagNKQ+w8f0O5zmLZnxmIJi8Ljsf/jOpvRT'
    'Ix+TjWvPasXuKFt6o2GmFbz0bqI74USeWmUUz4VXmi1VPPEouJRBfbKoE1Z5L+cU9yMRUOQKbONBTDkEfbj7u/Ds8ev3XbgVY7T3'
    'SpnOBM14fJ6FoK4l2fk27fpJAmcLY6HwxPCP8Nf59t/nezvYL/XkudwRvprDaYANC8zcxAOBeXvwfrh2rwJgsSpUWlZBjISX5Qk3'
    'eJuP4OJJZny6jIHTKHFw2Cf0gJlawdCZxVP8Bl6sQG44zIhCulxzoH8nYsrBy7Ix3Ek/kr3oGw6T/7oShYUMu8k8wINcDI3vgNoS'
    'BjWcH01ckJnPcU3Oi8Y5oOp5D6l0iEkEn0RK9nXhE9IfYi2ZzCd3MSp4J34hyTuJrKIzmDnnErddbaDz3vpklL8WHtvdoa3B7YJF'
    'vURD3FduxLJxWjpNrhPFUffs3SnnPEieAVtMn7BKMCjclhiLgz14XjzFwk5DGXGpcZ90E4zqhCcZB+ohIeMaFhrpU2uBcR8tHEea'
    'HiSCojndsJkD+bjYVm1VCWirv9amiPwaZOwqfDeyOtZvMSWQcKlgPf1YcFw8o/aQVQ1/dFNp1CK+CYtbiuXW2rPc1tRIhbH4aLoK'
    'Uh3FAc1TjYXNKrMfDNGCokesXsZveo2IvWyeKcT8+xh0SHeSBxcVhSHCQAPOHprEGROCPN3pNMzwZQUCjURGBzvN4PxErJy8Pzx7'
    '34U94nqfNnv2rPBsTAAIihcJvAYwEBrIRssG5n2O5JJi0ZZ7lSL2qvsbHC38Y+RNtvCq3ZIv3ZrnaxPWmli8vymX60f/wmwL3Hn6'
    'hi4W4sxHclPU43o6olp4ldY8gKRa/ggQ8Y7wklcSmBfB78xj7hR3kXmk+pGZN5XfBzI1AS/N3VMKivCoFxPZkeDS5FucLdiyCYoO'
    'W7S/tpBlXcWJv4Uo8rCDyALL2BW0sfFKpg7zKIstFC4xukZ2AWIufaIdu4ub23PpCxLPU0b4Q9GRTLDOMRzrlIRiJQwWdJFzSlsQ'
    'rt8Khg9OMLwrGN7Smdjo9YI5Zk0rv55xG139U51lvqM5JkrbJhWUPZ7pU/K9GZZwmQKCjyRiDDcxYQoY8qHuBm2in7CaaUg3vOwU'
    'n8Yu+xGLDDJzGJgAXBdkNs3zMlHxS9VdIZ06MIMXe+sQBDctBtYG+s+tkQzxr+Sx/+KURfOeltes0+8A5aSZjqRzfoLJpZAqgfsN'
    'g2sEA0Khipq83N3td2585yoxZul9CW+7m/tylYBBYwnMfa8BKfGZPIcrc/A2yTiZK4u9OGTPLMrJ9rsU/Sm/k1Pld6DVNixN7/PP'
    '7iPA1sJk8I87a/YB3ltAJ8PZ2ATVqf56uAtopzKYU0nZb7GdWmynFttpja7CFtupxXayoGmL7dSMXi22UwMBt8V2unWLSIvtVPb+'
    'bx7bydIe0wI8VU6xBXhaVXJtAZ4q4/dagKcW4KkFeGoBnlqApxbgaflzLcBTC/C0zgVrAZ4MorUAT38dgKc7gTnK1e57h3X0sOBj'
    'yn7GFkOmxZBpMWT+BBgysRf81SFkjg4ObRBkCo8tA5ApkdQeP0Y2tIOPMd/Sose0GC23gNFyfzF67gV6TIFBLACPKfEGtFa10DEt'
    'dEwLHfOXh44pcA9CjjEPKTxMiW/a4bFYaGkcw9kmv7fJ7zbJ720G0mrxNneYmk4Ft5ulXVMTAjRIAl9yH/QPA/XFtRdO8SBJc7yO'
    'TJNaI7/OYStaP3rMadtSEEol+noPrgV+cLuHURR4sSjrFEbvqQwb88ztyBitkO8qP/amYy2X4HmEY5DoyuNwIod4k6IX+Yod3ggn'
    'A8dko4bOO8EBeCh5+0XZuE3br3UuzESiMHEa+hSMlkaKLS8F9Wu4xMU1xt5mKkZKrlSO016dMM3BqAkI89zfMJ5GGulEteWssLDe'
    'wWB/dYyFH7hnNi7N+dB12bKUdIyTpV6dzEh4o1n1IyZZLbHyuPAzlANMwhC8gUYUoFdYUmWtAck6C7Ix3Y50GmZOt4v4Sl4KPI25'
    'TQULihk8pCV8O1MMfScnLQZuE9oX4yBi9CxhhGn6YqIrm8zzbENh5IQaef1ePJltLe+7H6EDBC+HtNi5hHEI6kN3LeMKOnIK9T5j'
    'HPZyT/HHO5Zubip72AJPFNNOye+0TjiJFvBhfbcSXsOz1TTF40LTWugH9j9CkyJOKsFm4YUOrDkUjrQqmIqTSg5oICa1qst9VF2S'
    'hhvsTN7GGlGWMHWnYcgiYxyh5Mm6OwVHpKBTmHzAsFBm7ug+JZeC4DvSKaZyUjsLIOhOxfgnGdU+H/9opKSCbL6VXrhPv3jx8h/f'
    '759+b5GIurbsKDG+rLkVqmjCM9NZejq+xR2leqVZIlH8Q64msoUg4oQ6araIdmfu6JaJ8CYIs9VIoRuzuRj4nLhWWjnrv/Qjxc0j'
    'hZgIktkSIYkUtzZfGETjacJ6FI8AdJLvf/Ps8krfOVO9MV7MDfGUdKi3gXZEJtjSxapuRcKChpNhYpVRohwVw5NE1z485ikmiJJh'
    'OixaC/0Y1PqEb250CLbX74O7ftF2HHhinwHWGtdlPJ1rrnNbjfX4Qe8ap9hAJ20akr/MruZdyTxAuhC04CcvAdyhCIaSud4Fd8MH'
    'gt6gMeNiboiGf+U945yITMGIjZVLSyW3czJS6eGX/Ug5vPIYJPxrl0IDJfzQLrfqqla7S1+RT1JNx3jL3FlLdzM3/ZTuKlFZdCex'
    '39VSsPG9pEFX0mD3P13f79LL8F3yVd0s7rrlRzdp7FoFJ4vTNkK8EVZGynLqkx3vCCBLpg7iVmiMbVW8Gh8GPNWKsbBuUdqXgF6u'
    'gS6jaIUASBKK1FXkbKomGpRiwKr1oCItJArIeMFw1oguP1ETa0EgS6ZkEZtMB2HgoY8y7UeK9fLruYtgFLkZeSngQJVtytpeI3Vz'
    '+IcM+2hA5cwtXBVmabhoiqWvyyiMNtajw+8ODiVrbW4cLvdQMk8onp2bc6E17AW0GtOUyVQcCkkycsSWtiJTilIt2TfL/tqDGD8i'
    '4UORAu3xE6alkZtWNd5K8xEQeKQY8woN5BsDBsR1o5nGwsnxx7lCRiJLZTjuCDdGVpjXxsp/mDQlIhuEZWBXTvnL6UZs3HDRqyGC'
    'sh70RI+HnaZT9NBL3q7cQCqVzPB2r7/yB7/btuhH2TPGAy8XBCqpbqV1UgeRpR+kqCKA1OfeTEMviOe9/KpLJaq7/Ygh496iiE9h'
    'pJiMKYtuNCx6YVuIxKIMSUcu4IpEPZXLfxOq6uOl9lID0lIEhULju1XS3rieiHVGmbn1Gyzo2jIhb7fgSR30Rb1XQ+5TDantEZvv'
    'NEPb0qjaxZ2dCe8iikFzn2klie6QOW/kulxaVoNHXVVmetyaV6vGwGZjS1luTykSvqCsVvgrgJXMi1P18H6NwN2sLCDrsoKswJX+'
    'uCHUgTU/qrGMNNlpN0Wck6t+EseWQZSVGl9FJ032H1zup8EI3dpaqv8Fsed6vxKUAwKHOaQyC6xxAF2w4CiR1eW1CGIjRg+yruTo'
    '/oJomLiw/lMKznUee5R7pS7Hg/0dx2jWj07EJwM8ZHsu5FBjr7sUFIkL6Tv9ztyol8MBt4fnoRyejRpI9XW8SSPpulNRHxDEcDEo'
    'nTE7zLD0eYThNcalrxVbOJ5mk2mWR3gVkYZLprV0FnktvnCLL9ziC9/oTmvxhVt8YQuatvjCDXXbFl+4kZuoxRe+XaG8xReeM6Ft'
    'FF+4IHK38MItvHALL9zCC7fwwi28sNPCC7fwwra2nxZeuIUXXtGp3sILt/DCNmJdCy9srzO28MJ2dLp1eOF7AyCsxnbYHOTlqNBU'
    'zVhPlnBeyLCqgV5M5COOBSAQJwrAZBgy18I9srbVfrcyPsZRVQ9zFJCQBurnNc2+RbrYtGm8RbpokS5WvqlXzpUjFvCTEVH1BsYp'
    'kgni5TZLm1vWk2JSQ+MreYzNaC50WFByQugsTeUoWWsL3sfAyAPhW1xlzSsLSSF+bBKHgTfb0c5ZiuwCIUKKBTtsF5ISZuGtynBf'
    'TmegiLTePUw5YvixqyiMXb+IvK9zPSoiTZqGlzwgjPyKJ667eYpilwLjNQR8FVtZEPCU24I7CjeaywxIPWVR3fhpSG0u3PQxxiUS'
    '6PS281//5RS+we62raOzLIdogpata5yqz227Ffv4Z69ZUFWeoJg8XFeUoMX8XzYZxuVHrPjqka9nqdo1Kle0kKPuTkI3Epw0oqex'
    '8cVcUtNhEidZTYUANRJMUC8jrGNz+O2rvfL3IBzEXkz1Es4OjsvNMjcZieyYG3PHjxawsSWDSReM5vnzZ2sdzqMKSbaTVmunuDWq'
    'l61yldVtexBieHxyeNxpVN9lklbWc/lOTMJ4hhCq7UF8KAcxgTUDgTstenYWbjNSyN9VrZ7VHjR3daGkCGh9mRiVk6z1Pj0RVOtB'
    'LNjNYjxBsJ65wS4KW11SQUid2zG676a8E+QB/Wrvq705uav0LAj3Lg8ZxZvOUjEprCbjMkLuVDy5+pG58bFZ4eisIGvMSXjF4jVV'
    'aPgdjcJgWVAGOPEiRaLT7QqsGZB2MdDvVaXkDc9c4cnoumHY1YcyfTVc6IeDFmE86oZYquAVhiIve4qQ5kFle/XrIk8GDpJysKBH'
    '1xdJlzHLFj8t5fAuRsG92qVTUvOk618yBeY2Ve+zxyc/fjg7fP/6lw/771+fHu8fvN7upZdez+P7pUfBwr15XaPCRtMR0WUzlU7X'
    'zCmPYZGSRP6EN3Bul6WJkHe9FjWLnlKVaXS0Sc6Wm+nYN1QcFSHOfnzzy8nR0dnS+eODu9l4sttLZUpeZ02vf3v0/vX7d4fvD89u'
    'tABKE3xjtRD6wEtQqQ7F1y7NLNdvoGC9AAuU9MZiXKh7tfKyWW11Qi/Bt48uvEQBPHn+7twJ+2+JqvjiyZPBi4HnPhOu+PqLgTcc'
    'Pv/yyfMnz/0nw8GT5+5zd/DVM//L4ZPn4sXe157nieHTgf/sq6+9J0+fDJ99WVkBiQZxPA3DY7K3EaTE8EOcHXNcVlUTvAoikabH'
    'STxY5EsgefatWGypVEkPnd0L4YbZxW8L07qUgCwfW9nGFNVujUq9pGbb650nBfmv975eEG21TKVZqDPc8FCWR4dCjMXouijW3NEQ'
    'v37+vHaINTvGYoBWBxSDPYM17nTsb7b5jb7MiCYPMHK7xQP2JlMcyJO9vb2Fu0CySnzsbWCfkapKQNW+/AubV794/j5YnU5UJCPI'
    'Zgfo57rOFhZFwyIax0lwGYRiJF6nIMsobyAJeJXz9NyJOwjCYKlftuMn8WSJX6yz/+5d9WX0sQHBXf8oCmeIAvAGZsBpSZUGWG1E'
    'jvbTD3GELZY9B+RDbQPOBub41Be6OplGGPz9ncw5XnnZLrFUpHiPVtmm1n9so8S1xVKvwWnomZsa9AtvzcaTupfiI2uwy89VLIx9'
    'sSS6oVNUyeKU5aIINLileuwkCWI6RaGbpkr8mquJWHvUOsP0raz0+uTZsy9rPQxzOKK12m4HVJFxENHZfYvJe8cChu6fYlSSTxaQ'
    'sj2Rd5qlDknht98FRNpl4kfVlrIpgmnbf8XuKe2LantMW+J50yWe9cv/JB4fNR+ZLb2Eto3qPC/r5zZLPbtUqC+xqPX8g0mIxbWe'
    'C48tq/VcJKx9qedPqV2V50L/D6PK8+1V/W2rPt9G1ed7UVu5cCAX1FYunkXK1GlrK7e1ldvayn/52soF7jFXW7lQYorgq93Qm+KR'
    'mi+93I9oiV0JBCGTsX/QctDNEK9IPH5vg+FTnuG3Zss5iG4tpzn0Bl3Uw8xe9H1E75P8BB/LjJqZDEiN1hUjtRI25RYjqeznSsAW'
    'EBATK+kLkXehqzQEiYqZ57bEpZwtSvvE9AmRmL3RiJb05hjtUo4znXDOKKFDj9cOh1Ag9BF9XdhMWDQaxD6EEiksicS7roE+sIq+'
    '7swRvTa8vpK4N8+PqovI3mB+FHK9OFrprBwUmpbyJLhfh7VG2pqGhssbjKt2c21wAnsIQ/Oo7EczR1yDzoCcgfrBjEYjS0pWNu5H'
    'ssiyLyLMgcerARExGbEdbyo5FpAf1pRWsjyaovzw/UMI2zeXItZsS0lBfIdspXnRotuCBVsYIXL/acoxQrdOzjvJ1NA2nqZAPKqZ'
    'wSw0kBv6jIh++S2bN7j5/XMPeK0vvGQ2aZxb+R03M5GLVXGmgRiiTGsCXo0VXp0KRVkPy2sC2F6Nv15RuConCAj6cBWLtaVVpfEk'
    'fegI6mfLq85MkuAShbmjiYiO3x4TTnqeYZmTFhSffRK6EfFDl6jjgsCwSeKpn5eeYQkMa5AjaIdRVBbkR1nskV0flBNHv3Sx5Eqp'
    'tHAuVs4XMMN8RxH6LSh1g6vmYSK6N6x9V7U6dvXvyiXpZModCJdG2Tvekz+8P1WPSytD8QSA3Hk4RBj4RQdmhJFA5WMTKDRn0Pzm'
    'jk5eXItgETUuvUzn4xeZ1SOd4lF7MHiFtwIivuRyDQVuGx3U1eSCNZuWASml58oZuckAU4A99GJ5zOY40RjTPOcMqzQexKD7iUra'
    'GMr+4633QZLEyXEyjajeOr0f/upHW/9yg+xNnJzlflt84CiZXLjR1nbPKTR1xvSBDwR9xRBJ/ehxTC1QHeKADTkc/AKjG6Cn78zi'
    '7WavNy7gbnS2XEvneS9/Zp4gy59nUt1NXXdfYKXE9KipeCdbkRE0r+rA3wPfmJ3o6nwpbNAca01+S0tY3H+5gYd4jKpdRdFYSmis'
    '2rdy62vYEn/tdp+qWWnwMxHF09FFAahagzabNzSyUkMa1mZm5h2MR8aGIuCmB6/fGVWkyNCQpiizsA1ZxrutEUvTUhZZjySyVpXW'
    'zK5ZZfjUtjyHYiFNdXeXHlUQ0tJHQLu2UH5Rr/wtk4SOzGvYPiuQ5ES1ZYdJeSPSHIt3jdyZEt+PdyYQBSQSx9cHp+cQwIWuTbiT'
    'm5q7QZQ3VOUj2U0Wul6Oy4wVqz1D2qcvi+ND0D2s9/ZJVPzosAHmUjimobvi7TsSa10wWMIID/L5vmwMfebs4AAfP9esSqJ1nONt'
    'dd57eOhedWL4vQfOAhbs1aIhqVoqC6NCqw/GG+ybgEARA6iq6nAi89/ym4zKoBKSEgPkDAl41p+qkrXBeDwlgN4CeO9mixJz3DLt'
    'XDzmzaxh35caM5PA6Blki9w1nSHj3DH2pkBhUiOB9iN+lpAAuaZUfv2r+qhkAH+dn993QJwpSrOP4RBuSyRO8z0oqMr3AIeIo3DG'
    '0i7KY2iHN0bPD2t2tH7kbJqU8cKCo0hOnilF2FIlGqzxZrcIaLAKbdCYMYWRMpa1Xl2bipdrveokmMwKUzuQMDRSN6+66BD+BkV4'
    'LJMgtXYKpKHbrYoYFy5JZ1x6vuw+vmXKIK8R/gqEeUMN104XHg/zSaDQndMnQIDhEc5rBRod6sZrpxMGhMzIAnM/9tHSSJuamJs7'
    '4hm3ICoZXNWSQz1kucqQGZrJC/taNjC0e/I2BpEXTv1ckJdXIisT4xo1cqUrOQ+RPSJK4g5dRZ9HWvq2Wj1aRaJZrj3eo4tdBSjO'
    '677ArJAL5YXkSzVIJ/QoMiTVhQxrIJ3w4fGnO7RctDYXY9+RsF7ceSC4u6htwcX4DuEJ+OiebMqwcgs3B+3XnT+5Ih40xyXO8Yhz'
    'hRKB8lh95B1B8QIc1mhgUvLL+pE/peBePwmGmYSuROEC4xdTIftyZeRBkIe65DcTp5z7/UhanIp2ZooHS3K7FyEl+yIvTfF/To8+'
    'OBT5C9INRYbIiFES4Yqj4t4wBEIBya79vmOCnsC0te7pEhXYD07+oEsBA/CDNBEjN/GNKhuSukxStoeVZ2Ax7oY3GtFsBZZyTFE4'
    'hZ1Da3Es1+LxyZsD58XXe0+284AdQjqWIgguEldqQ1egq6oSuOadJ+Pz6/mNzVKt5o63ZnVLD60dh2fUsxXW4owaymh7haFdOsFz'
    'ZKUV4XPNHh7apnxOMeL+cOjk/dIFISTSMi+9Ej+YE3AwCUZm5i9SVnqOHpYyJ5z3YGgU1y2cd4ulbhTuUQjBtIIvXyK9zXVUSG8g'
    '5XMYY8i2wrPHSNRUwQ0Zimo/UlkFxSRDP/ZSzCnACmLpLgarXgbiavcqTuD+GnWRiF1J0V0OgNz9TxBIYakyHcSqA2q0VNygautK'
    'R8TikBgpjKtQnpKflc6PQjR1lnNU4zZBrkIOiREXGSJyKGsasn9OS6E9TTgEIYlEU7j8B8FoGk9T4M2ylhIdG2izGytkevwiNxfm'
    'yziCt0wHVDUlX1EjT2QQxoPdsYtRduWcEcSHRkiRSZy6sJ6YLTJ20XAtkhl9orn2xv7dLZ2lsF8n8OPCvW22cPw4LptawuUrB6pf'
    'u3Rmn8Qlbsj33pl9PAyWx0/eIbezjjJcoGlmMc+ulIBzxzOy1T6Xa6ALT//dTe7S2qRTNbWSs+ZGfK69nqxtA83E8/oY1duxRLC6'
    '9fDNDO+DFD3GB6sleBxW97HU08/vNVI9lLqPuskwnkZk1pY3wABTsMfxpc510DYBWVgKFJZC+npv5o7DfiRD3pJpROHzpTzOzQYJ'
    'ENxgQzpSk6IW/pj6Iev3jhOJK+OvzB2hS57rhW/3I/KCo9UB55o3S3fwyTR/lPJRiSWBEB2mnLkEXEBg6SbiYG4/ooALVTMWs7ip'
    'pg6LDGmAZQVpGaVKun7Ly5hjblV51Mgx6eAalHDnabEjFWHSaWUMFKdkUeanG3IYOXJoaLdG64ss3d5c5f+OGiqliHPrlZGscgJM'
    'DRw9qfa+bi+T7J0P4urMVWn68L3U6x+QfZ6OAcyQM03y5b/tKYirDyvOgls2WNW7mR7sk9VmhxvMfnK1R60N6NvIBS8r4DS6ic6o'
    'YLcsxwNqoTQsxnmIeIW1T5ZrNsv4uBNgn9cBltTiWtJcFD6dynjf2Pk1wBKJ5AyI0in6IMRwGHiE+DFNRcHvvTynsVCEFqvD/o2q'
    'zdJf2988Hqe/p7+Pf7/Y3v7bZ5usjIUy+QFBYjSm+A+6KZlfFa1V5l/Rl4IWMJKKsjznU9bAo2MYYHVx0DMiIzVvDsijN59ptUOC'
    'hCeqhDaqz4WRyxduOGQNCTaH7MORnThcxB5TB8nenA/ukFWqbldGkHZlSlZXZXANQ+YoZJvGOH1mK6Zr3HFT6UvhPohSNvNi1ygr'
    'Y7UFxBtkyDL8yXt3skqu54HRWFaWRSAjlcOgst1cRz9YjJGXYdZktCEJV8zSl/2oH3Wdc5WXdf5S5o3KrDVYRyBkzzniWt7n7lV6'
    'vgP//AanD/8YeRP4J076EQz4nATswDvvOSeSZ/aod7mqsvPhNARV9n+nbsg+Z227MfP1TFcCdC17UNErpdw6hJ9yPsQyq096E/Vo'
    'qAP1bD40XuNYTcz30V51joLhuYeAatm54f3geaiHeB7y0/yIyQ5A9b6M19EocP8ZVHoj0bRisgfo/ML5iJAdPiTYAxUCVa8OCmnc'
    'OSXNQ8CgL8GQmhs9BjLnh61Nkg7GvES5e+pAvaJHnzAPcuoHnGFk+opKp5D7lU8qELHinslXiLcML8FLWaNT7vHj1++57gP0erDv'
    'eHjqhpy6aXa6YCkOh0VnlsGvaLx4haguyr0rHbJMahqtcz6fx1oe+pLNXeQ/iuopNsjTYDgRVGMIIWH1lipmVucTLWZ/5NOtemsh'
    'pIh3u1rZ8lTyJXdN7VOahlMxcVnLHsz47MZjhE+T9qorxMfiSiC7IE+G5ChXsHLGwhWHRx1l8ScRFbMS6aDrs6u6md9UmkdpNTTw'
    'VL7lsPoUymwanBKjJRT5CDLO99MMuFg4U1WcL2UGsc7fbTPYG2gXDzWDfVXsBr1Lll7mEt2hmO1GVV9pr/GljnKkJ4VBlLddQ9GS'
    '7IBaKHGJ2lAPcOilcETwX1vUZKvnLNraphDSI18MpY7hGcckLZ8HWhoTl6cedlVRA3knZRq8QiagERQrvFOi8+E1mKe8p0bNW7r/'
    'URKEY98ltoAOJ9g8CPJHsoE+5Ofe2KeCPufEJp0LEWLVZp462Q+nkael3nhKlysF4aA4jJi5NFZzHJLvHMdytjT2dILxLJRbVBTH'
    'MX92LmA17TmnGr2MMmcUF5KsK2c062UhsOorcZAfcPdEBmRBZfggmd4moRgrtM2uXgclgsttaBe5uoGgnbXwUCZBy0FvE4FqyZMN'
    'qyCr/2rYtVFyWFyDNguHVErJVC041917plrnyNgr83d9R+Spq+rI1J3uudrF5ru2nf94ZdQwVm/ZXm0tPjY2X+AeOgZ5IrhuZL74'
    'oJsxF57w3zrtmy4++F7Gh1radMbu9TsRjQjN+ene3rIng0g/+WSD1h2czOl0uAp5uBmTJ+W//3TkmXAQRyPanHJNTLhPxiIZsZ2Q'
    '44C5sx2dsO6i+orahfN/99+/U4GPO/3IcK6z0YkkfBmtOHBTupAdjHzakVEtRWRKHWa5/hDiY1LFC44snoKe9nuaNbAYnPSLr/ee'
    'OtL3puQpaUcjIw71xiojujeNQOz1BhF7F6sFEVvNlWdBqJ7qieLcpRiM/kk0euO6sv+RDJ+8rrfsJ7lpNC8FtafzAfNatuaJ+7E3'
    'HRPadQ4tbLnEbTxtG0/bxtO28bRtPG0bT9vG07bxtG08bRtP+wDjaUHzeMjhNrIErr36i+l3Si3wgUp4j8zKoM/zwa3kFEAXGLux'
    'EDcNjsIkRBBJ1I7JoTDfKlcr8sjZYYyurwIw6IeYIEpl2A+Wv6ASSVp9ieOM4nW18ZROVY137ObWhTjNqIBIMwKrVg7/MNB1XVxP'
    '10IApQnBKhSIOtkXVG5jP8ppNZhx7HB5YYARAZsM3XVFlRRKND68qginevjKEQbUnOBu+SRmuxzVM3GDJJUQZJduEiA7T01wwhls'
    'quJKKFxTuvwRFERuPwx76UclXEN8ofKA5+T0c4EIzwy707BkFCUyp6oADfluBm56oaQ5GdJIurlyL8E7RW/Ucz77N4z/5SvpDvlj'
    'R34B25XW5Q+6u+g7Lr2JHe4aHf5xa4U2cjq8wbrnjd2bheZyaYuAtNqZyD62U1mxIOdn7N3MF1xauYJE+e45s9xcsaDiUKqdkwdG'
    'KXOZhN+m4jQEjq8rj0kHaqLC4mULUIyMqBn5DO5EL3QTcz+pTaj8enqMjHADIoU7mYjatGfr/PbF5K8A3XHzhaBQvVzeX0x7HQbP'
    'x2D95qU1KcdyZ+QwJ5fz4Nq87AibrbfE1ral1GxZXkI+zW+y6tkxQvw6Fs9/fLA6WfVK9ZxTFjhgMyI8fnUcFIc29CPGRDLldMv1'
    'KzhCvnhm18bOJbJhsqvoEHvSW2KvLl6uIxWQAgeMIuFQHGJ1q4S1rTkIsUcqykUSp348xgCTkEQjCtd1BylBCmF4CiL4ap5c1Wkg'
    'n4c+CQcFg99cDfOXxz26eVILZiNR7O5OHtkBUsCc9NBQWa7J8VqnwtXAnW8HdGTp+LdgLc2UQUuBpRZHxVZekS6k2Q1kFtVFseCg'
    '+pIAVvSFThVO1a5aJH+USzxQ5LXTdf4Fe/Mn3fqxEa2+/dKROwCj5GHTYZhllF/JUviR23iHwhNFIM9mQqh6GaVmkNOMROriL3hs'
    'wksTXK8klVGXhmTWoxHvh1fuLH2p1aA56UZccpW9KDZFt0TYnjjrCk4F2tULJDzwWyv5dCdl1yZUUqORyktFQUTEyzRfwWSzma+w'
    'rZLZ4ZrTjqBLkGnhIrgM2M4nwXB1VJ7KQfrXXAjbXGT4NJWHfz5vRA27H7GSqt+Nr5smDyQHqWEJpqplqI5tn6u5hJncYwy+BIkC'
    'y/tSAGExcQnueWtUqJvPXBmiGk04V6dUaSkpewDjFfMGOA7IDdJ1lRW1RyFtgEG6zvpRS+9oKx1vHdih1nfI0cHhiSDrS5zM6u+Q'
    't0HW5PFvp94nC/Wv8/qaq8nvY8qJWydQ3VZdwmiVemyr5BqsdcR2vrV11qYx83lKkMQ3KVNzb6q21aoWNUrFJmu6pdMU03Qa3llw'
    'z1D+aCbCsCp5VfZKci0QCfXJ3HovroVHki6GEwaZ48eCU98YYJTKVHMZrTRzKcI/b1FMXyK9fLMCFseifbA6F9XhaPnJSNE6C0qE'
    'LKYt0tJxCGSe1AIPlHV86otn9yA8NQvGIp5mzQjGbUg/zOPQd+TGQE3KLEVCgacqVDEtu9WUdLmFqLD1wtB9ESev3KAZzahazDL0'
    'Hy7bYoDWy/hn5qWqCl3OeVNZ/IpVGinRz9WiURgnGzqPjxpQzYYP59AMNaqfhbT7qAGPtuDPlbPqcOmNhTvBME4u2irwSsrc9d+y'
    'R5X3S/dJI9KWRcmCEkdDLFh41Cu59Adn4H2yUUjsRHgEAGD/a03Y+0o1kFTfubjhi4xKYCE/QtORi3pultcJ4ZI8eq6kf6GacGJl'
    'Um8UJx66aXaGwQE0RGSUKzi15jtRsaz4i4MsWzEQSYpMPy2Bp4kOvDm5Khil/So8kjzkQdZtldVTuHR63i0DdgP3IOu1TAJEEeBT'
    'FF9FxHIiWViLovKDsdEjUtgsQEbFfzCZcULFySxca1wrAymCiZJd7P52I9zz3KimSyhbcvTjxXTscj1AMmjq39jZQOjycge7g3jK'
    'Ptl8RdWiSaAY6Ins/dILb0FGU+Z49vTLF1/dKg0r2VtTcs53kruw+WT0xkBCdHD3RvkzOpMg39LoO8EoB06BmU6IvohQgXezC+oK'
    'wVJU9oYhdsxLQMp58lQhwcG7+aD1crb38/XHXsWYoYevd0oDQiC5KTErn81FXNGWWZhUxSpYmNADbnSQ4H598dxiywRRMCbLwp71'
    'ZsGre7Ss5rXNboFDkq60Q7ih6fufYC0tdzym6uUyBDIgcBV97GR1UWyoAhj0wmylktuaB/E4if2ph4nVMj+S6xrkfBhowSeVr1sM'
    'aIZ1FLlLBBGfQKKCt6ugCVTSkE3ucLVe0/FoePNVHQHM+XJGUxdGlQn4gKAwKmAIrbNGkoxzACpLeAAbXfEKyUmYK+MokZdjzYI6'
    '8J8KTvJk7+lzm31k71EuCPc/73f/x+3+9vGx/AME/F92Xn783Pj4cfubz273PqiR9hbvTnkTK4lE7ZcdlWp7lkyB8bzhAuU/RnS9'
    'WqyHdZBGB19g4zalIdg8KAe5PhfrWjLSuK+mq4PNqGZozpQj4/DQ5QCHNe6Jaxfz/ikwWv/e9AZ+8qLRQXj8M293OAld+dfn6itQ'
    'eFH5XfbA9ue78JRxij7+3M2PUO/j59vfGL9tf/bw4AgrRG5Lsc7uLrLjCTY780EX6wtS8gU0quvLbcxLWQZlp5E7gZsq0yyRrtqi'
    '49LBQwAXEyK6JS7bkfjCvgxSYp6q9mUeVKNsSNgt1QOVfaw9h/lUTsAUQ13OaO0GEakqNJ3EZ+2aExALFQuLs0UbKwXc0jSDMQEW'
    '59UCd6QyxxGaLqhrwf9OhQa51dLN/UPuJbtWOh2rkBGeknP+Dzccxf98+Y8Lcf3P89wboahDT6OqKgl923VuEYDuRJvdVil4W+xB'
    'kcPUkQlRhzcz6SWMepcb+7T4L+EiH4DGjOf4RmR75zalWoF1/AmI9t10ZTX5XWVHREQyIqFCGX+aB62dP3aKwr27pMTpquL2u4pu'
    '1FYqiuIV907vtm1MbGmwmeaKaS0bwJcqEfy9nIRx1euhFore5gauFRj7WqIw48wNTwoLvsoOO6voRjMr/M0B1WwAajxd+cXHyCp1'
    '4V6CZuGRZcfPLQENqNLYqNPMUHMLkruUMBpexc1uoNVY7ypsapWN97BR1C9B6myqExyqVsVoEYWuurjqdSF8F04QphbBERoIEArS'
    'KWEkMuSyBIdZUySawOxmK3G5OM/X3M56ThvLkFJOLsRlK5DcZMuRQPq5ycyoSu6aQMtU3dJtIFQ1TYsKVk2KOvwuv9lVWiJrZFoT'
    'LAVslhZhK3XUHUxKmKmlbP1Dh3388xf6G/4hXQ7+xXihf27dJQrBDfEHDICcUsTkUmrhvHv3NX2/WTZJYJVLcvlQE0k2Gi6nOOOd'
    'xMPhDbzPjP6IqqmcSIWlcVQ3aQBVF4gs05KrQv3oNcL5p0YNl1wTVajysq2KcM0h1Y18r1OFqf5jyujDKplLptpraXpRp2gDYtzu'
    'VKN2c6fkgdpxKAcbhcqjg0NQ+7bMijRumsZe4Bbyvj9hxm+/EyejHrDtSCEYJ2mPigz11DT7nY2GqhuruoH1rF7Ikxus4MZpwdbL'
    'FanxrqoHxfTLG3eJAXbj0/we9nOIQ5QS9X7WeJ7zXchU/Hzfy4mOY56oQLj93AyCXA+tlvTsjpNiujjHreiNkWNj0kOIsRlxalpG'
    'Pt6N0qlhGMVchmtlMMLcwsPWzgMels7HXvu01TubBRNaBOw9suirpp9iH6X2HSYptMbE3vJvoONw6FDVj9OBNrlVLKPhZy4N4FHV'
    '3wrRmL+Rg1R9FlNpOpdP9EqpLJVOsQZF/nulZYoR4sqjhrdMekWgNk+VscRX6Kjybh70WtgyFR2o+BYSdTxv+imKr7u+CAOQVWd1'
    'jSduknVjTHnqDMPpdd3jlwaFnvae7PX28p1grLpKFambTyFBo2LwDRYMxpruVq3ad2ISxjPESmlXjFes0EKOujsJXcoU7RjTuI2l'
    '1WuCUULF9UCYm8Bz02JMTCetRl3sEAbLu6o1ZMIsHHQlszCnjLc7gljNvXGRSdrAxq3kW6D0jzF6acorGie0lb7a+2pv7n4oPQuX'
    'lcuMGNllZynbDatpUUONnYqHb3QAbnwIVjgIK7CvuXujcEzmdqc+PCz/VyiB80IHaKKjRVUIOt0uJspnaRfrF72qlBPgmSvc5F1Q'
    'hrr6fKWvhguDkaBFGGMZ1EsRvkJD1rKnqJQWCF2vfl0UzoGDpDQK6NH1RdJVgKSLno7irpfEaZqPtgvaQfoqWxRmxW24NmEXY0+X'
    'P7ugGuCrqyAFSe2qq+W1CmmqQu0GXf1ywfosyFtQ3PDkxw9nh+9f//Jh//3r0+P9g9eLEgNIJK5B0OpQ4GFtJjI9dcyggZoX9XK+'
    '20x+tE3lqCHE26P3r9+/O3x/eHYjCiix740VJfQ5lPnqHS6GkHSWmm/4DZRIEIyDLO2NYdslszXQzWqvkcUA3z668BLkTsjFPH+3'
    'iqH+d3rhPv3ixctnX/qDp18Pnn7hu+LZF4OvvnrifiH2XjyH5fYHe5739RfPnz9/6rvPv3jmPvtauO6ecAdful/v+QPhec+rzhGP'
    '43gahscxXLczshUPP8TZMRtbqpogk45Emh4n8WBRIGEHQVLfLsG9V3iXnV1O5PptYS6NvB/VYyvrMFHt7qB3pc1YgN58xzxOvMZ3'
    'lh8SJA2Cv46XpA9lsReHZKw5OO7c8HCWh/j18+e1Q6xZE4sBWp0CzPYI1riXKNN281tpmVoqjwiylMUD9iZTHMiTvb29hbtA8iN8'
    '7G1gn2snTTRWL7d494vn74PVCQX38DQJstkBbEFxvWgFOy5inR8nwSXc1SPxOvXcUBlvFqKVdQjIOQiDpd6zjp/Ek2WplPvv3i3I'
    'gWxAcdc/isLZSRxnb2AG6SwFnaHSpqFaTKP99EMcYYtlzwH5UNqGw4Ep04snqcwzJyD9BGMhs1hXX7bLOJyOxXsUphqywzG2UVLJ'
    'bjaedGo4DWpXlvxjqdWpxF06UeyLJQj9naJqEKcsCESgSSzVqiZJENOGDt00VfJGZ87iVbfrO8P0razc8eTZsy9r7WdzmDw2ihfQ'
    'NhnLMt5vExASjgWM3j9FqdjHCb8oXQNy3S3VGUqH+S4g6i67b6tWuLR21Tp4A/tPMnC9HpZ0hMWRubmfvmKlr8IodBKHos4cpEaf'
    'U7eLHv+wiwUab2LpwCJuRQqXDE4B7Yz5RZBJ270sjsNPQdZjgRHmWF52vTUqHn204MQUrrTSez9f3AqmOKhtUWVVsZ3zSgPm4nfl'
    'WCNZcH3sTtJO9RGT+mPaeL6jOVifDobqlL+7KoPU3z5p2MrQeIJAT7SAlZnhWufjxXHiS3YlT+9KU0RwRLHhNdyxIQ9Xrq0mWulL'
    'YBdwFd31qbE8BKoPwoKZ72e59cVqLQxkuAU0eWR+s+674duASn3f3RUBYyhbPfRyL52S+dbK26522POW+SnXCVp8ZdV4yAov5Z2z'
    '0FtiR6nFZ6LJUOp9N9ajabAbb+5aVOOvOGc32HOwm2IS3ouDOcN62koNu1NBTE2X0KSxiJWvXXuWB87zoc04XqdIhn7HlZhtPvgb'
    'M9p13HSVl5K8v+4/A97k1rgVVlw7gQ1z5aWsZHVG+Aj/+uP/A3Bra6M='
))
assert hashlib.sha256(CONTROLLERS_BYTES).hexdigest() == '316c166b0a1290cba17f464e0f5b52d8a5edf2107a69327b186e9e03fe17cb95'

DEMO_BYTES = zlib.decompress(base64.b64decode(
    'eNrNV0tPGzEQvvMroj0TyIaAgBsibYUU6ApoLxUHxzshVrxr149AWu1/73hDkt1gg6GVaA5Esef1zXwzHn7vdDoJkew7KM1EmZx2'
    'knma7LrTGStz93vEtFmeMAOFxqMf+KPT+V3/DanXNysTV6QALQmFzVUBhuTEELxeGcLTEgWdAqHUzkrx2KV5N4dCrPVQhpMxcN3S'
    'w1Mp8q4GahUzi72ZHYMqwYDeY2IfyolQtLarQBvFqIG8YTFKuztvQtw7OIo28EBU+U7fTvW547VytdP8rnbfWpYbUHNG4YxSYUsT'
    'W5sHhtGKhy6RslmWcl1jX/1Wka59EGtE4dy2g7gVM3DxTgjXEAELg9D7PmxDkFwsCngzrr/ApCXQtm2FUTBKHFvThl0NHKgRapvE'
    'BTF0OvLxuwYum2E2LqsNIxpOsFklJwaeOfFlIdxZr/huem/59+XjCfyS6+eiNPBofO6ULc/0lSivhXD3RlnY9cp80+CSmPZ6vdQv'
    '8UUJK4Mik1fuMVYqCpkpMWEcPKG6PC9kzY9rpC8rYAgTYrlJtgSrds7anhKKuSCsRF6vx+vm4/EZ5uxahBXkvilzij4w8Qo7ojvv'
    'd/u9/lGapifdtD84DupnlvNMIIUXztLF5EqYDOdYs6tak0wZHwA/iBaQqTHSY7KdnAzto/BgcHLikayend15YnydfUvCcy4eMsXm'
    'WPZ7+KQpwVZazpx6NPlCxW4n+deSLxxtP6OiXmhswgCBl9CIJGPGmWGgA6GgVK6EDKS1vj8bjRLv3V1UmipPmrDIwuKzF4oKBX5a'
    'fNBeiJpK6yp72CtChS1wiqqaWUeDS+aDUHmzxlnBIjz3o1yn/eOA76hEaUOUsW5CjCGUK0PljaAzMOGQ5ZLayz6IToQExUR+g+1d'
    '5i4ffa/UhDBuFdxOsahTwd3zmB5GsoDk2Hhafww8VmJjED4EThYbkAdRqUh7UQg5m8P/BjDtxRW7F1vtg6hUzAW3BVy6LeydQ1wt'
    'X8BgzznTGTFTJ7uPwvvefSI4zV98Ubdm/ROaNz6nYQAJLlNmMWQqxBHNfsHIzaV6pvgmSvWm+GP2493txaopeeVZ1/0747/5L+Ij'
    '1+zVCnbOLb646iJLIpbt0E7b3KF9G83WOvvCBrOaCsdbnZrgm3EPJgvMjE1p7tql2XEn1R/sh5Dd'
))
assert hashlib.sha256(DEMO_BYTES).hexdigest() == '08789ff48f065ff175a75546a1c27f376d2d868c1f033c7ab5066838c7da3a01'

K = ['kubectl', '--context', 'kind-wisecow-ci']
NS = 'accuknox-delivery'
NAME = 'wisecow-delivery'
OLD = 'sha256:e95cb63bb9ff2b2fcb0e37b1372d66ed61344cbfe4382251a3ec33c0928ff5db'
BASE = 'ghcr.io/alonerider-pixel/accuknox-wisecow-qa-assignment@sha256:97eff69859ec73ad7cf1b9efadb25fada344539e41b1f7641cff42541b8c574e'


def run(args, obj=None, timeout=200):
    return subprocess.check_output(K + args, input=json.dumps(obj) if obj else None,
                                   text=True, timeout=timeout)


def read(ns, kind, name):
    return json.loads(run(['-n', ns, 'get', kind, name, '-o', 'json']))


def await_status(kind, predicate, timeout=180):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        obj = read(NS, kind, NAME)
        if predicate(obj):
            return obj
        time.sleep(2)
    raise RuntimeError(json.dumps(obj.get('status', {})))


def is_ready(obj):
    return obj.get('status', {}).get('observedGeneration') == obj['metadata']['generation'] and any(
        c['type'] == 'Ready' and c['status'] == 'True' for c in obj.get('status', {}).get('conditions', []))


def normalized(spec):
    s = copy.deepcopy(spec)
    s['template']['spec']['containers'][0].pop('image')
    a = s['template']['metadata'].get('annotations', {})
    a.pop('qa.accuknox.example/source-commit', None)
    if not a:
        s['template']['metadata'].pop('annotations', None)
    return s


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true', 'CI only'
    assert os.environ['GITHUB_REPOSITORY'] == 'AloneRider-pixel/accuknox-wisecow-qa-assignment'
    assert run(['config', 'current-context']).strip() == 'kind-wisecow-ci'
    assert len(json.loads(run(['get', 'nodes', '-o', 'json']))['items']) == 1
    controllers = json.loads(CONTROLLERS_BYTES)
    demo = json.loads(DEMO_BYTES)
    assert not any(x['kind'] in ['ClusterRole', 'ClusterRoleBinding'] for x in controllers['items'])
    assert all(x['metadata'].get('namespace') != 'accuknox-qa' for x in controllers['items'] + demo['items'])
    deployment = next(x for x in demo['items'] if x['kind'] == 'Deployment')
    deployment['spec']['template']['spec']['containers'][0]['image'] = BASE
    for fixture in [controllers, demo]:
        print(run(['apply', '-f', '-'], fixture), flush=True)
    for n in ['source-controller', 'kustomize-controller']:
        print(run(['-n', NS, 'rollout', 'status', 'deployment/' + n, '--timeout=180s']), flush=True)
    print(run(['-n', 'accuknox-cd-demo', 'rollout', 'status', 'deployment/wisecow', '--timeout=180s']), flush=True)
    before = read('accuknox-cd-demo', 'deployment', 'wisecow')
    source = {'apiVersion': 'source.toolkit.fluxcd.io/v1', 'kind': 'OCIRepository',
              'metadata': {'name': NAME, 'namespace': NS}, 'spec': {'interval': '5m', 'timeout': '60s',
              'url': 'oci://ghcr.io/alonerider-pixel/accuknox-wisecow-qa-assignment', 'ref': {'digest': OLD},
              'layerSelector': {'mediaType': 'application/vnd.cncf.flux.content.v1.tar+gzip', 'operation': 'extract'}}}
    ks = {'apiVersion': 'kustomize.toolkit.fluxcd.io/v1', 'kind': 'Kustomization',
          'metadata': {'name': NAME, 'namespace': NS}, 'spec': {'interval': '5m', 'retryInterval': '1m',
          'timeout': '60s', 'path': './', 'sourceRef': {'kind': 'OCIRepository', 'name': NAME},
          'serviceAccountName': 'wisecow-reconciler', 'prune': False, 'deletionPolicy': 'Orphan',
          'force': False, 'wait': False}}
    print(run(['create', '-f', '-'], {'apiVersion': 'v1', 'kind': 'List', 'items': [source, ks]}), flush=True)
    failed = await_status('kustomization', lambda x: any('spec.selector: Required value' in c.get('message', '') for c in x.get('status', {}).get('conditions', [])))
    assert read('accuknox-cd-demo', 'deployment', 'wisecow')['spec'] == before['spec']
    print('PASS: actual same-controller Flux reproduces missing-selector rejection; baseline unchanged', flush=True)
    print(json.dumps(failed['status']), flush=True)
    print(run(['-n', NS, 'patch', 'kustomization', NAME, '--type=merge', '-p', json.dumps({'spec': {'suspend': True}})]), flush=True)
    print(run(['-n', NS, 'patch', 'ocirepository', NAME, '--type=json', '-p', json.dumps([{'op': 'replace', 'path': '/spec/ref', 'value': {'tag': 'deploy-' + os.environ['GITHUB_SHA']}}])]), flush=True)
    src = await_status('ocirepository', is_ready)
    assert src['status']['artifact']['metadata']['org.opencontainers.image.revision'].endswith(os.environ['GITHUB_SHA'])
    print(run(['-n', NS, 'patch', 'kustomization', NAME, '--type=merge', '-p', json.dumps({'spec': {'suspend': False}})]), flush=True)
    applied = await_status('kustomization', lambda x: is_ready(x) and x['status'].get('lastAppliedRevision') == src['status']['artifact']['revision'])
    print(run(['-n', 'accuknox-cd-demo', 'rollout', 'status', 'deployment/wisecow', '--timeout=180s']), flush=True)
    after = read('accuknox-cd-demo', 'deployment', 'wisecow')
    assert after['metadata']['uid'] == before['metadata']['uid']
    assert normalized(after['spec']) == normalized(before['spec'])
    assert after['spec']['template']['metadata']['annotations']['qa.accuknox.example/source-commit'] == os.environ['GITHUB_SHA']
    pods = json.loads(run(['-n', 'accuknox-cd-demo', 'get', 'pods', '-o', 'json']))['items']
    pods = [p for p in pods if not p['metadata'].get('deletionTimestamp')]
    assert len(pods) == 1
    c = pods[0]['status']['containerStatuses'][0]
    assert c['ready'] and c['restartCount'] == 0
    print('PASS: actual Flux corrected full desired state reconciled; rollout Ready; same Deployment UID; all other spec settings preserved', flush=True)
    print(json.dumps({'source': src['status'], 'kustomization': applied['status'], 'pod': pods[0]['metadata']['name'], 'image': c['image'], 'imageID': c['imageID']}), flush=True)


if __name__ == '__main__':
    try:
        main()
    finally:
        for kind in ['ocirepository', 'kustomization']:
            subprocess.run(K + ['-n', NS, 'get', kind, NAME, '-o', 'yaml'], check=False, timeout=30)
        for n in ['source-controller', 'kustomize-controller']:
            subprocess.run(K + ['-n', NS, 'logs', 'deployment/' + n, '--tail=25'], check=False, timeout=30)
