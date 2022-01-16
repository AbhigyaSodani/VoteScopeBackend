f=open("comments.txt","r")
a=open("polls.txt","a")
comments=f.readlines()
c=open("num.txt","r")
num=int(c.readlines()[0].replace("\n",""))


if(num<len(comments)):
    counter=num
    while(counter<len(comments)):
        print()
        print(comments[counter])
        print()
        conversion=input()
        if(conversion=="quit"):
            d=open("num.txt","w")
            d.write(str(counter))
            d.close()
            break
        print()
        a.write(conversion+"\n")
        counter+=1
a.close()
        
