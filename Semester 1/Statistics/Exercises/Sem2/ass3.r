lambda <- 7
n <- 100
x <- 0:(6*lambda)
plot(x, dbinom(x, size = n, prob = lambda/n), ylab = "")
points(x, dpois(x, lambda), col = "red")
