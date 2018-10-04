n = 10000

set.seed(27092017)
x=rnorm(n)
x2=x^2
y=cbind(x,x2)
cov(y)
cor(y)
plot(x,x2)
