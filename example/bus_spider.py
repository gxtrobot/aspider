'''
define url routing process logic
'''
from aspider.routeing import get_router

router = get_router()


def verify_page_path(path, no):
    print(f'verify page {path} , args {no}')
    no = int(no)
    if no <= 10:
        return True
    else:
        return False


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
    print(f'process item {fanhao}')


if __name__ == "__main__":
    from aspider import aspider
    import sys
    aspider.main()
