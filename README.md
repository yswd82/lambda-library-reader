# 概要
📚 lambda-library-reader
lambda-library-reader は、東京都内の一部自治体（杉並区・中野区・練馬区・港区）の図書館システムから、貸出中アイテムと予約中アイテムの情報を自動取得するための Python ライブラリです。 AWS Lambda コンテナ環境での運用を前提に設計されており、サーバレスかつ定期的な情報収集・通知の自動化に最適です。

🔍 主な機能
貸出情報の取得：タイトル、カテゴリ、貸出日、返却期限、予約件数、延長可否などを取得

期限切れ判定：返却期限を過ぎているかを自動判定

予約状況判定：他利用者による予約の有無を判定

AWS Lambda 対応：コンテナイメージとしてデプロイ可能、スケジュール実行も容易

🛠 技術的特徴
Python製：データクラスやプロパティを活用した読みやすく拡張しやすいコード構造

サーバレス設計：AWS Lambda + Dockerfile による軽量デプロイ

自動化志向：定期実行や通知システムとの連携を想定

💡 想定ユースケース
図書館の返却期限や予約状況を自動でチェックし、Slackやメールで通知

家族やチームでの貸出状況共有

個人の読書管理ツールやダッシュボードへの組み込み

このライブラリを使えば、図書館の利用状況を「見に行く」から「自動で届く」に変えられます。 詳しくは GitHubリポジトリ をご覧ください。


開発環境、使用ライブラリ
Python3.12
Windows10 Home 22H2



Overview
📚 lambda-library-reader lambda-library-reader is a Python library that automatically retrieves information about items currently on loan and items on hold from public library systems in selected Tokyo wards (Suginami, Nakano, Nerima, and Minato). It is designed to run in an AWS Lambda container environment, making it ideal for serverless, scheduled data collection and automated notifications.

🔍 Key Features
Loan Information Retrieval: Fetches details such as title, category, checkout date, due date, reservation count, and whether the item can be renewed.

Overdue Detection: Automatically determines if an item is past its due date.

Reservation Status Check: Detects whether other users have placed a reservation.

AWS Lambda Ready: Deployable as a container image, with easy scheduling for periodic execution.

🛠 Technical Highlights
Python-based: Clean, extensible code structure using data classes and properties.

Serverless Architecture: Lightweight deployment with AWS Lambda + Dockerfile.

Automation-Oriented: Designed for integration with notification systems and regular execution.

💡 Example Use Cases
Automatically check due dates and reservation status, then send alerts via Slack or email.

Share loan status with family members or teams.

Integrate with personal reading management tools or dashboards.

With this library, you can shift your library usage from “checking manually” to “getting updates automatically.” For details, see the GitHub repository.

Development Environment / Libraries

Python 3.12

Windows 10 Home 22H2