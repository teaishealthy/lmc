loop    LDA sum
        ADD value
        STA sum
        LDA value
        SUB one
        STA value
        BRZ done
        BRA loop

done    LDA sum
        OUT
        HLT

value   DAT 100
sum     DAT 0
one     DAT 1