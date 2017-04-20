# MacAutoPac
Update Automatic Proxy Configuration automatically according to Wi-Fi name for macOS.

## Install

#### Homebrew

```bash
$ brew install macautopac
$ sudo brew services start macautopac
```

## Configuration

#### Example

```
[autopac]  ;; default section
;; pac_url = http://example.com/path/to/proxy.pac
;; static_addr = 127.0.0.1

[ExampleWiFiName]
;; pac_url = http://another.com/path/to/proxy.pac
;; static_addr = 10.0.0.1
```
