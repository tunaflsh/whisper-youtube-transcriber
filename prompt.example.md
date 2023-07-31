# Practices for Prompting Whisper Model

## Example

```shell
-p "Cast: Koseki Bijou, Shiori Novella, Nerissa Ravencroft, Fuwamoco, Fuwawa and Mococo, Yagoo and other members of Hololive. Starting... Intro music"
```

## Notes

- Empty prompt generally works well. Suboptimal prompts might make it worse.
- Refrain from using special characters s.a. `()`, `[]`, `~`, `&` etc.
- Indicate the start of the audio, e.g. `Starting...`
- Use `Intro music` to indicate the audio starts with music with no speech.
- Don't use `Intro music playing...`. The model tries to recognize music during the speech.
- Keep the prompt short
- Specify language with `-l` flag. Performes much worse without it.
