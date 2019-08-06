## Building

```docker build . -t cw-testing-server```

## Configuring

First make sure the udevadm rules are changed on the host. Just follow the ChipWhisperer installation where the *plugdev* group is created.

## Running

```docker run --privileged -v /dev:/dev -e EMAILS="email@example.com, another@email.com" cw-testing-server```

The tests should be run as a cronjob every 4 hours starting at 6:00 until 18:00, and e-mail will be sent to all the emails specified after the tests are complete. Check your spam!
