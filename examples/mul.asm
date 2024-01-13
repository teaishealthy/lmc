        INP
        STA a
        INP
        STA b

loop    LDA a
        ADD sum
        STA sum
        LDA b
        SUB one
        STA b
        BRZ end
        BRA loop

end     LDA sum
        OUT
        HLT

one     DAT 1
sum     DAT 0
a       DAT 0
b       DAT 0