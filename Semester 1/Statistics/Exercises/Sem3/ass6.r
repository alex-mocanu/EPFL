set.seed(04102017)
N <- 1e5

dims <- c(1, 2, 4, 12, 25, 100, 250, 500)

# Store proportions for Student's t distributions
small <- numeric(length(dims))

for (i in 1:length(dims)) {
    X <- rt(N, df=dims[i])
    small[i] <- sum(-1 < X & 1 > X) / N
}

# Store proportions for normal distributions
X <- rnorm(N, mean=0, sd=1)
small.norm <- sum(-1 < X & 1 > X) / N

plot(dims, small, xlab="Degrees of freedom", ylab="Proportion")
abline(h=small.norm)

xval <- seq(from=-6, to=6, length.out=1000)
plot(xval, dnorm(xval), type="l", xlab="", ylab="")
for (i in 1:length(dims))
    lines(xval, dt(xval, df=dims[i]), col=i)
plot(xval, dnorm(xval), type="l", xlab="", ylab="")
