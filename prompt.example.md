# Practices for Prompting Whisper Model

## Example

```shell
-p "Cast: Koseki Bijou, Shiori Novella, Nerissa Ravencroft, Fuwamoco, Fuwawa and Mococo, Yagoo and other members of Hololive. Starting..."
```

## Notes

- Refrain from using special characters s.a. `()`, `[]`, `~`, `&` etc.
- End the prompt with `Starting...`
- Keep the prompt short
- Specify language with `-l` flag. Performes much worse without it.
