FROM golang:1.21.4-alpine AS builder

COPY main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags='-w -s' -o /hello main.go

FROM scratch
COPY --from=builder /hello /

USER 65534:65534
EXPOSE 8080
CMD ["/hello"]
