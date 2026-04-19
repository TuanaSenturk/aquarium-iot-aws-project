# IoT Tabanlı Akvaryum Sıcaklık ve pH İzleme Sistemi

Bu proje, Bulut Bilişim dersi kapsamında geliştirilen gerçek zamanlı veri akışı ve işleme uygulamasıdır.

Projede fiziksel bir IoT cihazı yerine Python ile yazılmış bir sensör simülatörü kullanılmıştır. Simülatör, belirli aralıklarla akvaryum sıcaklığı ve pH verisi üretir. Üretilen veriler MQTT protokolü ile AWS IoT Core servisine gönderilir. AWS IoT Core üzerinde tanımlanan IoT Rule, gelen mesajları AWS Lambda fonksiyonuna aktarır. Lambda fonksiyonu veriyi işler, pH değerini analiz eder ve sonucu Amazon DynamoDB tablosuna kaydeder.

## Proje Mimarisi

```text
Python Sensör Simülatörü
        ↓ MQTT
AWS IoT Core
        ↓ IoT Rule
AWS Lambda
        ↓
Amazon DynamoDB
