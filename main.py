import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from github import Github

TOKEN = 'YOUR_TELEGRAM_TOKEN'
GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'

github = Github(GITHUB_TOKEN)
repos = {}  # {chat_id: [repo_names]}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет! Добавьте репозиторий командой /add_repo owner/repo')

async def add_repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        repo_name = context.args[0]
        chat_id = update.message.chat_id
        if chat_id not in repos:
            repos[chat_id] = []
        repos[chat_id].append(repo_name)
        await update.message.reply_text(f'Добавлен {repo_name}')
    else:
        await update.message.reply_text('Укажите репозиторий: /add_repo owner/repo')

async def list_repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in repos:
        await update.message.reply_text('Ваши репозитории: ' + ', '.join(repos[chat_id]))
    else:
        await update.message.reply_text('Нет репозиториев')

async def monitor(context: ContextTypes.DEFAULT_TYPE):
    for chat_id, repo_list in repos.items():
        for repo_name in repo_list:
            repo = github.get_repo(repo_name)
            # Пример: проверка новых issues (можно расширить)
            issues = repo.get_issues(state='open')
            # Логика уведомлений (здесь упрощено, добавьте кэш для новых)
            context.bot.send_message(chat_id, f'Обновление в {repo_name}: {issues.totalCount} открытых issues')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('add_repo', add_repo))
    app.add_handler(CommandHandler('list', list_repos))
    job_queue = app.job_queue
    job_queue.run_repeating(monitor, interval=60, first=0)
    app.run_polling()
