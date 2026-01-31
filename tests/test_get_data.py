import pytest
from unittest.mock import patch, mock_open
from ..lib import get_data

def test_make_url():
    urls = get_data.make_url([2021, 2022])
    assert urls == ['https://www.gein.noa.gr/HTML/Noa_cat/CAT2021.TXT', 'https://www.gein.noa.gr/HTML/Noa_cat/CAT2022.TXT']

def test_make_filename():
    urls = ['https://example.com/CAT2021.TXT']
    filenames = get_data.make_filename(urls)
    assert filenames == ['Data/CAT2021.TXT']

@patch('requests.get')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.exists', return_value=False)
def test_get_earthquakes_download(mock_exists, mock_file, mock_get):
    mock_response = mock_get.return_value
    mock_response.text = 'sample data'
    mock_response.status_code = 200
    get_data.get_earthquakes([2021])
    mock_file.assert_called_once_with('Data/CAT2021.TXT', mode='w')
    mock_file().write.assert_called_once_with('sample data')

@patch('os.path.exists', return_value=True)
def test_get_earthquakes_skip_existing(mock_exists, capsys):
    get_data.get_earthquakes([2021])
    captured = capsys.readouterr()
    assert '2021 earthquake data already downloaded!' in captured.out