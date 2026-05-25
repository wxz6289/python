from app.config import Settings


def test_dotenv_overrides_exported_shell_env(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DEEPSEEK_API_KEY=sk-from-dotenv",
                "DEEPSEEK_BASE_URL=https://api.deepseek.com",
                "DEEPSEEK_MODEL=deepseek-chat",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-from-shell")
    settings = Settings(_env_file=env_file)
    assert settings.deepseek_api_key == "sk-from-dotenv"
