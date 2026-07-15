$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$DemoDir = Join-Path $ProjectRoot "data/demo"
$EventsFile = Join-Path $DemoDir "learning_events.jsonl"
$StudentsFile = Join-Path $DemoDir "demo_students.json"

New-Item -ItemType Directory -Force -Path $DemoDir | Out-Null

if (Test-Path $EventsFile) {
    Remove-Item $EventsFile
}

@'
[
  {
    "student_id": "demo-lower-primary",
    "stage": "lower_primary",
    "interest": "animals"
  },
  {
    "student_id": "demo-high-school",
    "stage": "high_school",
    "interest": "programming"
  }
]
'@ | Set-Content -Encoding UTF8 -Path $StudentsFile

Write-Host "Demo progress reset."
Write-Host "Seeded students: demo-lower-primary, demo-high-school"
