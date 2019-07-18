'''
define url routing process logic
'''
import sys
from aspider.routeing import get_router
from parser import parse_item
router = get_router()
counter = 0


def verify_page_path(path, no):
    print(f'verify page {path} , args {no}')
    no = int(no)
    if no <= 10:
        return True
    else:
        return False


def check_exit():
    if counter > 10:
        raise KeyboardInterrupt()


@router.route('/page/<no>', verify_page_path)
def process_page(text, path, no):
    '''
    process list page
    '''
    print(f'page {no} has length {len(text)}')
    print(f'process page {no}')


@router.route('/<fanhao:[\w]+-[\d]+>')
def process_item(text, fanhao):
    '''
    process item page
    '''
    global counter
    counter += 1
    print(f'process item {fanhao}')

    meta, tags = parse_item(text)
    print('meta keys', len(meta.keys()))
    print('tag count', len(tags))

    check_exit()


if __name__ == "__main__":
    from aspider import aspider
    import sys
    aspider.main()
