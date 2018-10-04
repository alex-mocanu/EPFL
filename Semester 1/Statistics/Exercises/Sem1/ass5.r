n = 1000

set.seed(20092017)
X = runif(n, 0, 1)

quant <- function(x, lambda) {
    return(-log(1 - x) / lambda)
}

Y1 = quant(X, 1)
Y2 = quant(X, 2)
Y3 = quant(X, 4)

E1 = ecdf(Y1)
E2 = ecdf(Y2)
E3 = ecdf(Y3)

cdf1 <- function(x) {
    x = pmax(0, x)
    return(1 - exp(1 - x))
}

cdf2 <- function(x) {
    x = pmax(0, x)
    return(1 - exp(1 - 2 * x))
}

cdf3 <- function(x) {
    x = pmax(0, x)
    return(1 - exp(1 - 4 * x))
}

par(mfrow=c(1,3))
curve(E1,-1,5)
curve(cdf1,-1,5,add=TRUE,col="red")
curve(E2,-1,5)
curve(cdf2,-1,5,add=TRUE,col="red")
curve(E3,-1,5)
curve(cdf3,-1,5,add=TRUE,col="red")
