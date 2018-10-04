# Poisson tasks
set.seed(27092017)
n = 1000
X = rpois(n,2)

mean_est = mean(X)

mean_out = 0
M = 10
for (j in 0:M)
    mean_out = mean_out + j*dpois(j,2)

mean_out1 = 0
M = 10
for (k in 0:M)
    mean_out1 = mean_out1 + (1-ppois(k,2))

# Gamma tasks
set.seed(27092017)
n = 1000
X = rgamma(n,shape=3,rate=2)

mean_out = 0
for (i in 1:n)
    mean_out = mean_out + X[i]/n

mean_outs = rep(0,10)
for (j in 1:10) {
    set.seed(27092017)
    n = 5^j
    X = rgamma(n,shape=3,rate=2)
    mean_outs[j] = mean(X)
}
plot(c(1:10),mean_outs,type="o",xaxp=c(1,10,9),xlab=expression(log[5](n)),
ylab="Est. mean")
abline(a=1.5,b=0,col="red")

Sfun <- function(x) {
    return(1 - pgamma(x, shape=3, rate=2))
}

mean_new = integrate(Sfun, 0, Inf)
mean_new
