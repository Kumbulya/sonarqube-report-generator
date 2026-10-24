// ==========================================
// CODE SMELL: Использование var вместо const/let
// ==========================================
var express = require('express');
var crypto = require('crypto');
var cors = require('cors');

var app = express();

// ==========================================
// SECURITY HOTSPOT: Включение CORS для всех доменов (*)
// ==========================================
app.use(cors({ origin: '*' }));

// ==========================================
// SECURITY HOTSPOT: Жестко зашитые секреты (Hardcoded Secrets / Credentials)
// ==========================================
const DB_PASSWORD = "SuperSecretPassword123!"; 
const AWS_KEY = "AKIAIOSFODNN7EXAMPLE";

// ==========================================
// BUG / SECURITY HOTSPOT: Отключение проверки TLS/SSL сертификатов
// ==========================================
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// ==========================================
// SECURITY HOTSPOT: Небезопасные настройки Cookies (нет httpOnly, нет secure)
// ==========================================
app.use(express.session({
    secret: 'my-secret',
    cookie: { 
        httpOnly: false, 
        secure: false 
    }
}));

// ==========================================
// VULNERABILITY: Использование опасной функции eval()
// ==========================================
app.get('/execute', (req, res) => {
    var code = req.query.code;
    // SonarQube CE железно подсветит использование eval как критическую уязвимость
    var result = eval(code); 
    res.send(result);
});

// ==========================================
// SECURITY HOTSPOT: Использование слабых хэш-алгоритмов (MD5 / SHA1)
// ==========================================
app.post('/login', (req, res) => {
    // MD5 и SHA-1 считаются криптографически взломанными
    var md5Hash = crypto.createHash('md5').update(req.body.password).digest('hex');
    var sha1Hash = crypto.createHash('sha1').update(req.body.password).digest('hex');
    res.send(md5Hash);
});

// ==========================================
// SECURITY HOTSPOT: Предсказуемый генератор случайных чисел
// ==========================================
app.get('/reset-token', (req, res) => {
    // Опасно для генерации токенов безопасности, Sonar потребует crypto.randomBytes
    var token = Math.random().toString(36).substring(2);
    res.send(token);
});

// ==========================================
// SECURITY HOTSPOT: Уязвимость ReDoS (Regex Denial of Service)
// ==========================================
app.get('/validate', (req, res) => {
    // "Жадное" регулярное выражение с вложенным квантификатором (вызовет зависание CPU на длинных строках)
    var unsafeRegex = /^([a-zA-Z0-9_-]+.)+@([a-zA-Z0-9_-]+.)+[a-zA-Z0-9_-]+$/;
    var isValid = unsafeRegex.test(req.query.email);
    res.send(isValid);
});

// ==========================================
// CODE SMELL: Пустые блоки, закомментированный код, дублирование
// ==========================================
function unusedFunction() {
    // TODO: написать реализацию
    if (true) {
        if (true) {
            // Слишком большая вложенность (Cognitive Complexity)
        }
    }
}

// app.get('/old-route', (req, res) => {
//     res.send("Закомментированный код — любимый Code Smell для Sonar");
// });

// ==========================================
// BUG: Сравнение, которое всегда истинно / недостижимый код
// ==========================================
function checkValue(x) {
    if (x === x) { // Бессмысленное сравнение
        return true;
    }
    console.log("Этот код никогда не выполнится (Dead Code)");
}

app.listen(3000); // SECURITY HOTSPOT: Не отключен заголовок x-powered-by 