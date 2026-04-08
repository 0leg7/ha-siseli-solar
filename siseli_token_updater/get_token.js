#!/usr/bin/env node
/**
 * Siseli Solar — получение токена через headless Chromium.
 * v0.2.0 — добавлен retry при таймауте навигации
 * Записывает результат в /config/siseli_token.json
 */
const puppeteer = require('puppeteer-core');
const fs = require('fs');

const ACCOUNT = process.env.ACCOUNT || '';
const PASSWORD = process.env.PASSWORD || '';
const TOKEN_FILE = '/config/siseli_token.json';
const CHROMIUM_PATH = process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium';
const MAX_RETRIES = 3;

async function tryGetToken(attempt) {
    console.log('[' + new Date().toISOString() + '] Попытка ' + attempt + '/' + MAX_RETRIES + '...');

    const browser = await puppeteer.launch({
        executablePath: CHROMIUM_PATH,
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',
        ]
    });

    let token = null, refreshToken = null;

    try {
        const page = await browser.newPage();

        page.on('response', async (response) => {
            if (response.url().includes('/apis/login/account')) {
                try {
                    const json = await response.json();
                    if (json.code === 0 && json.data) {
                        token = json.data.accessToken;
                        refreshToken = json.data.refreshToken;
                    }
                } catch(e) {}
            }
        });

        await page.goto('https://solar.siseli.com/', {
            waitUntil: 'networkidle2',
            timeout: 90000
        });

        await page.waitForSelector('input', { timeout: 20000 });
        const inputs = await page.$$('input');

        if (inputs.length >= 2) {
            await inputs[0].click({ clickCount: 3 });
            await inputs[0].type(ACCOUNT, { delay: 50 });
            await inputs[1].click({ clickCount: 3 });
            await inputs[1].type(PASSWORD, { delay: 50 });

            const buttons = await page.$$('button');
            for (const btn of buttons) {
                const text = await page.evaluate(el => el.textContent, btn);
                if (text.toLowerCase().includes('sign in') || text.toLowerCase().includes('login')) {
                    await btn.click();
                    break;
                }
            }

            await new Promise(r => setTimeout(r, 8000));

            if (!token) {
                const data = await page.evaluate(() => {
                    for (var i = 0; i < localStorage.length; i++) {
                        var k = localStorage.key(i);
                        if (k.includes('iot_token')) {
                            try { return JSON.parse(localStorage.getItem(k)); } catch(e) {}
                        }
                    }
                    return null;
                });
                if (data) {
                    token = data.accessToken || data.access_token;
                    refreshToken = data.refreshToken || data.refresh_token;
                }
            }
        }
    } catch(e) {
        console.error('[' + new Date().toISOString() + '] Ошибка: ' + e.message);
    }

    await browser.close();
    return { token, refreshToken };
}

async function getToken() {
    if (!ACCOUNT || !PASSWORD) {
        console.error('ACCOUNT и PASSWORD не заданы!');
        process.exit(1);
    }

    console.log('[' + new Date().toISOString() + '] Запуск Chromium...');

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        const { token, refreshToken } = await tryGetToken(attempt);

        if (token) {
            const result = {
                access_token: token,
                refresh_token: refreshToken || '',
                updated_at: new Date().toISOString(),
            };
            fs.writeFileSync(TOKEN_FILE, JSON.stringify(result, null, 2));
            console.log('[' + new Date().toISOString() + '] Токен обновлён: ' + token.substr(0, 8) + '...');
            return true;
        }

        if (attempt < MAX_RETRIES) {
            console.log('[' + new Date().toISOString() + '] Жду 10 сек перед повтором...');
            await new Promise(r => setTimeout(r, 10000));
        }
    }

    console.error('[' + new Date().toISOString() + '] Не удалось получить токен после ' + MAX_RETRIES + ' попыток!');
    return false;
}

module.exports = { getToken };

if (require.main === module) {
    getToken().then(ok => process.exit(ok ? 0 : 1)).catch(e => {
        console.error(e);
        process.exit(1);
    });
}
